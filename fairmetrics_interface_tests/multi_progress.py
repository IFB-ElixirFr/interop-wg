#!/usr/bin/python3
# -*- coding: utf-8 -*-


from multiprocessing import Pool, freeze_support, RLock, Lock, Array, Manager
import random
from tqdm import tqdm
import time


def test_bar(id, position_holders):
    total = random.randint(50,125)
    position = get_position(position_holders)
    with tqdm(
        total=total,
        unit_scale=False,
        unit='b',
        leave=False,
        desc='Position #%s' % (id),
        position=position) as pbar:

        for i in range(0, total):
            pbar.update(1)
            time.sleep(random.randint(1,10)/100)
    time.sleep(0.5)
    release_position(position_holders, position)


def get_position(position_holders):
    position_lock.acquire()
    position_index = list(position_holders).index(0)
    position_holders[position_index] = 1
    position_lock.release()
    return position_index+1

def release_position(position_holders, position):
    position_lock.acquire()
    position_holders[position-1] = 0
    position_lock.release()


def init(tqdm_lock, p_lock):
    tqdm.set_lock(tqdm_lock)
    global position_lock
    position_lock = p_lock


if __name__ == '__main__':
    maxrows = 10
    m = Manager()
    position_holders = m.Array('i', [0] * maxrows)

    p = Pool(8, initializer=init, initargs=(RLock(), m.Lock()))
    res = []

    for i in range(1, 1000):
        res.append(p.apply_async(test_bar, args=(i, position_holders)))
        time.sleep(0.01)

    [x.wait() for x in res]
    # Other threads output isn't tracked by this thread, so add newlines to move below the progress bars.

    print("\n" * maxrows)
