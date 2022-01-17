import subprocess
import time
import sys

polling_rate_seconds = 2

def run_cmd(cmd_lists: list[str]) -> bool:
    """
    Execute shell commands in parallel, lock main process until completed

    Parameters
    ----------
        cmd_lists: list[str]
            List of shell commands. All commands are to be executed in parallel.

    Returns
    -------
        success : bool
            True if all commands end successfully, False otherwise
    """

    task_list = []
    process_lock = True

    try:
        for cmd_str in cmd_lists:
            cmd = cmd_str.split(" ")
            task_controller = subprocess.Popen(cmd, shell=True)
            task_list.append(task_controller)

        while process_lock:
            process_lock = False # reset lock
            for task in task_list:
                return_code = task.poll()
                if return_code == None: # if any task is incompleted, set lock
                    process_lock = True
                elif return_code != 0: # if any task fails, stop the pipeline
                    print("Task failed {}, stoping".format(task))
                    for task_to_kill in task_list:
                        task_to_kill.kill()
                    return False

            if process_lock: # wait before rechecking
                time.sleep(polling_rate_seconds)
    except e:
        print(e)
        return False

    return True

if __name__ == "__main__":
    task1 = 'echo "foo" "bar"'
    task2 = 'ls -la'
    task3 = 'pwd -PL'

    # run these two in parallel, wait until both are completed
    step1 = run_cmd([task1, 
                     task2])

    # stop the program if step failed
    if not step1:
        sys.exit(-1)

    # run this one alone, wait until completed
    step2 = run_cmd([task3])
    if not step2:
        sys.exit(-1)
