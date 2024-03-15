import requests
import json
import logging
import time
import sched
import os

# Initialize scheduler
scheduler = sched.scheduler(time.time, time.sleep)
CURR_DIR = os.path.dirname(os.path.abspath(__file__))

def send_request_and_log(url, payload, filename):
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    headers = {'Content-Type': 'application/json'}
    succesful_response = os.path.join(CURR_DIR, 'successful_response.txt')
    request_error = os.path.join(CURR_DIR, 'request_errors.txt')
    unexpected_errors = os.path.join(CURR_DIR, 'unexpected_errors.txt')

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_text = response.text

        if response.status_code == 200:
            # Save successful response to file
            with open(succesful_response, 'a') as f:
                f.write(json.dumps(response_text) + '\n')  # Write response with newline character
            # Log successful request
            logging.info('Request successful. Response: %s', response_text)
        else:
            # Log unsuccessful request
            logging.error('Unsuccessful request for file %s. Status Code: %d, Response: %s', filename, response.status_code, response_text)
            # Also log in error log
            with open(request_error, 'a') as f:
                f.write('Unsuccessful request for file %s. Status Code: %d, Response: %s\n' % (filename, response.status_code, response_text))

        return response_text

    except requests.exceptions.RequestException as e:
        # Log error
        logging.error('Error in request for file %s: %s', filename, e)
        # Save error to file
        with open(request_error, 'a') as f:
            f.write('Error in request for file %s: %s\n' % (filename, e))
        return None
    except Exception as ex:
        # Log other exceptions
        logging.error('Unexpected error occurred for file %s: %s', filename, ex)
        # Save error to file
        with open(unexpected_errors, 'a') as f:
            f.write('Unexpected error occurred for file %s: %s\n' % (filename, ex))
        
        return None



def process_data(input_file, last_position):
    accepted_file = os.path.join(CURR_DIR, 'accepted_files.txt')
    rejected_file = os.path.join(CURR_DIR, 'rejected_files.txt')
    filename_file = os.path.join(CURR_DIR, 'accept.txt')
    url = "http://35.209.180.131:5000/invocations"  

    with open(input_file, 'r') as f, \
            open(accepted_file, 'a') as accepted_f, \
            open(rejected_file, 'a') as rejected_f, \
            open(filename_file, 'a') as filename_f:

        # Move the file pointer to the last position
        f.seek(last_position)

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 3:
                filename = parts[0].split('/')[-1]
                distance = parts[1]
                confidence = parts[2]

                if distance != 'NA' and confidence != 'NA':
                    distance = float(distance)
                    confidence = float(confidence)

                    if confidence > 4:
                        decision = 'accepted'
                        accepted_f.write(line)
                        filename_f.write(filename + '\n')
                        accepted_f.flush()  # Flush the buffer to write changes to disk
                        filename_f.flush()  # Flush the buffer to write changes to disk
                        print(decision)
                        # Send request and log response
                        payload = {
                            "bucket": "unai-videodata",
                            "video_path": "celebv_text/video/{}".format(filename),
                            "landmark_path": "celebv_text/trail_files"
                        }
                        response = send_request_and_log(url, payload, filename)
                        if response is not None:
                            print("Response:", response)
                    elif confidence < 2:
                        decision = 'rejected'
                        rejected_f.write(line)
                        rejected_f.flush()  # Flush the buffer to write changes to disk
                    else:
                        payload = {}  # Assigning a default value
                        if distance > 8:
                            decision = 'rejected'
                            rejected_f.write(line)
                            rejected_f.flush()  # Flush the buffer to write changes to disk
                        else:
                            accepted_f.write(line)
                            decision = 'accepted'
                            filename_f.write(filename + '\n')
                            accepted_f.flush()  # Flush the buffer to write changes to disk
                            filename_f.flush()  # Flush the buffer to write changes to disk
                            payload = {
                                "bucket": "unai-videodata",
                                "video_path": "celebv_text/video/{}".format(filename),
                                "landmark_path": "celebv_text/trail_files"
                            }
                            response = send_request_and_log(url, payload, filename)
                            if response is not None:
                                print("Response:", response)
                    if decision == 'accepted':
                        print('{} is accepted.'.format(filename))
                        print(filename)
                    else:
                        print('{} is rejected.'.format(filename))
                else:
                    decision = 'rejected'
                    rejected_f.write(line)
                    rejected_f.flush()  # Flush the buffer to write changes to disk
                    print('NA values found, {} is rejected.'.format(filename))
            else:
                decision = 'rejected'
                rejected_f.write(line)
                rejected_f.flush()  # Flush the buffer to write changes to disk
                print('Incomplete data found, {} is rejected.'.format(filename))

        # Record the new last position
        last_position = f.tell()

    return last_position


def process_data_periodically(last_position):
    input_file = input
    last_position = process_data(input_file, last_position)
    # Reschedule the function to run after 30 seconds
    scheduler.enter(30, 1, process_data_periodically, (last_position,))

input=os.path.join(CURR_DIR, 'scores.txt')
# Get the initial last position
with open(input, 'r') as f:
    last_position = f.tell()

# Schedule the first execution
scheduler.enter(0, 1, process_data_periodically, (last_position,))
# Start the scheduler
scheduler.run()