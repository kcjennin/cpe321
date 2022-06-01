import csv
import time
import bcrypt as bc
import nltk
from nltk.corpus import words
import multiprocessing as mp

# get all the words in the nltk corpus that are 6 to 10 characters long
SIX_TO_TEN = [word.encode() for word in words.words() if 6 <= len(word) <= 10]


def read_input(filename: str) -> dict[str, str]:
    """Reads the input, probably from `shadow.txt` and makes it a dictionary

    Args:
        filename (str): name of the file to read

    Returns:
        dict[str, str]: dictionary that maps users to the salt and password
    """
    with open(filename, "rb") as f:
        users = {}
        for line in f.readlines():
            # split each line into the user and the hash
            user, hash = line.strip().split(b":")
            # save the salt and the whole thing separately
            users[user] = (hash[:29], hash)
    return users


def init_worker(pi, t, ts, f, d) -> None:
    """Workers need to start with these values

    Args:
        pi (mp.Value): this is where the correct password should be saved
        t (bytes): the result of salting and hashing the password
        ts (bytes): the salt for the password
        f (mp.Event): if the word was found, so we can end early
        d (mp.Event): flag to indicate that no more looking needs to be done
    """
    global plain_index, target, target_salt, found, done
    plain_index, target, target_salt, found, done = pi, t, ts, f, d


def worker(num: int, word: str) -> None:
    """Checks a single word against the salted and hashed password

    Args:
        num (int): index in SIX_TO_TEN
        word (str): the word
    """
    if not done.is_set():
        if bc.hashpw(word, target_salt) == target:
            plain_index.value = num
            found.set()


def main():
    # read the info from the input file
    hashed_pwds = read_input("data/shadow.txt")
    plain_pwds = {user: None for user in hashed_pwds}

    for user, hash in hashed_pwds.items():
        # start a timer
        tic = time.time()
        salt, whole = hash

        # initialize the variables for the workers
        m = mp.Manager()
        found = m.Event()
        done = m.Event()
        plain_index = m.Value("i", -1)

        with mp.Pool(initializer=init_worker, initargs=(plain_index, whole, salt, found, done)) as p:
            results = {}
            # check every single word in the set
            for i, word in enumerate(SIX_TO_TEN):
                results[i] = p.apply_async(worker, (i, word))

            # every second give a status update as long as we didn't find the
            # password
            while not found.wait(timeout=1):
                running, successful, error = 0, 0, 0
                toc = time.time()
                for key, result in results.items():
                    try:
                        if result.successful():
                            successful += 1
                        else:
                            error += 1
                    except ValueError:
                        running += 1
                rate = (successful + error) / (toc - tic)

                # display progress on a line
                print(''.join(' ' for _ in range(200)), end='\r')
                print(f'Running: {running}', end=' ')
                print(f'Successful: {successful}', end=' ')
                print(f'Error: {error}', end=' ')
                print(f'Rate: {rate:.0f}', end=' ')
                print(f'Estimated completion time: \
                    {time.strftime("%H:%M:%S", time.gmtime(running / rate))}', \
                        end='\r')

            # if we found the password, we can stop looking
            print()
            done.set()
        
        # save the password if we found it
        if plain_index.value > 0:
            print(f"The password for user [{user.decode('utf8')}] is [{SIX_TO_TEN[plain_index.value].decode('utf8')}]")
            plain_pwds[user] = SIX_TO_TEN[plain_index.value]
        else:
            plain_pwds[user] = None
            print(f"Didn't find a password for user [{user.decode('utf8')}]")
    
    with open("data/task2.csv", "wb", newline='') as f:
        w = csv.DictWriter(f)
        w.fieldnames(plain_pwds.keys())

        w.writerow(plain_pwds)
        


if __name__ == "__main__":
    print(len(SIX_TO_TEN))