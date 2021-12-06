"""Example script to show best practices for concurrent calls to Private AI Docker container"""

import multiprocessing
from multiprocessing.dummy import Pool
import functools
import requests
import time
import orjson
import argparse
import statistics


TIMEOUT = 600


def equal_chunks(seq, num):
    """Yield n equal-sized chunks from seq."""

    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def worker(text, args, session):

    data = {"text": text, "key": args.api_key, "accuracy_mode": args.accuracy_mode, "api_endpoint": args.api_endpoint}

    if args.fake_entity_accuracy_mode != 'none':
        data['fake_entity_accuracy_mode'] = args.fake_entity_accuracy_mode

    stt = time.time()

    request_obj = requests
    if session is not None:
        request_obj = session

    attempt = 1
    while attempt <= args.max_attempts:
        try:
            r = request_obj.post(url=args.api_endpoint, json=data, timeout=TIMEOUT)
            break
        except Exception as e:
            print(f'Exception encountered during POST request!!! Attempt {attempt} of {args.max_attempts}')
            print('Exception is: ', e)
            attempt += 1

    assert attempt <= args.max_attempts, 'Max attempts exceeded'

    total_time = 1000 * (time.time() - stt)

    assert r.status_code == 200, print(r)
    decoded = orjson.loads(r.text)
    assert 'pii' in decoded, print(decoded['message'])
    assert decoded['output_checks_passed'], print('Checks for input failed!!!\n====================\ntext\n====================')

    return total_time


def make_request(d, args):
    sess = requests.Session() if args.reuse_connections else None
    func = functools.partial(worker, args=args, session=sess)

    # Use thread pool instead of process pool
    if args.num_threads > 1:
        with Pool(args.num_threads) as p:
            latencies = p.map(func, d)
    else:
        latencies = [worker(text, args, sess) for text in d]

    return latencies


def process_list(a, args):
    for i in range(args.repeats):
        chunks = equal_chunks(a, args.num_processes)

        func = functools.partial(make_request, args=args)

        with multiprocessing.Pool(args.num_processes) as proc_pool:
            stt = time.time()
            latencies = proc_pool.map(func, chunks)
            total_time = time.time() - stt

        latencies = [item for sublist in latencies for item in sublist]
        latency = statistics.mean(latencies)
        throughput = len(a) / total_time
        print(f'Test run {i}: {len(a)} requests took %0.2f seconds, which is %0.2f requests/sec, with a latency of %0.2f ms' % (total_time, throughput, latency))


# Benchmarking
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq_length", type=int, default=128, required=False, help="Length of synthetic data, in case no data file is supplied")
    ap.add_argument("--num_examples", type=int, default=200, required=False, help="Number of examples/iterations to test")
    ap.add_argument("--num_threads", type=int, default=16, required=False, help="Number of threads to use per process")
    ap.add_argument("--num_processes", type=int, default=8, required=False, help="Number of processes to use")
    ap.add_argument("--accuracy_mode", default='standard', required=False, help="Accuracy mode to use")
    ap.add_argument("--fake_entity_accuracy_mode", default='none', required=False, help="Fake entity accuracy mode to use")
    ap.add_argument("--print_fake_data", action='store_true', required=False, help="Print fake entity data")
    ap.add_argument("--api_endpoint", default='https://n1fan2hnhf.execute-api.us-east-1.amazonaws.com/deidentify_text', required=False, help="API endpoint to test against")
    ap.add_argument("--api_key", help="API key to use for testing")
    ap.add_argument("--reuse_connections", default=True, help="Re-use HTTP connections. This can enable higher throughput, but can be less stable in Python")
    ap.add_argument("--max_attempts", type=int, default=3, required=False, help="Maximum number of attempts for POST request")
    ap.add_argument("--repeats", type=int, default=1, required=False, help="Number of times to re-run test")
    args = ap.parse_args()

    print(f'Testing {args.num_examples} examples')
    test_sentence = "word " * (args.seq_length - 4)
    dummy_array = [test_sentence, ] * args.num_examples

    process_list(dummy_array, args)
