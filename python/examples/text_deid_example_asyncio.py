"""Example script to show best practices for concurrent calls to Private AI Docker container"""

import asyncio
import requests
import time
import json
import argparse
import statistics

ap = argparse.ArgumentParser()
ap.add_argument("--seq_length", type=int, default=128, required=False, help="Length of synthetic data, in case no data file is supplied")
ap.add_argument("--num_examples", type=int, default=200, required=False, help="Number of examples/iterations to test")
ap.add_argument("--accuracy_mode", default='standard', required=False, help="Accuracy mode to use")
ap.add_argument("--fake_entity_accuracy_mode", default='none', required=False, help="Fake entity accuracy mode to use")
ap.add_argument("--print_fake_data", action='store_true', required=False, help="Print fake entity data")
ap.add_argument("--api_endpoint", default='https://n1fan2hnhf.execute-api.us-east-1.amazonaws.com/deidentify_text', required=False, help="API endpoint to test against")
ap.add_argument("--api_key", help="API key to use for testing")
args = ap.parse_args()

verbose = True
sess = requests.Session()


async def make_request(text):
    data = {"text": text, "key": args.api_key, "accuracy_mode": args.accuracy_mode}

    if args.fake_entity_accuracy_mode != 'none':
        data['fake_entity_accuracy_mode'] = args.fake_entity_accuracy_mode

    stt = time.time()
    r = sess.post(url=args.api_endpoint, json=data)
    total_time = 1000 * (time.time() - stt)

    decoded = json.loads(r.text)
    assert 'pii' in decoded, print(decoded['message'])
    assert decoded['output_checks_passed'], print('Checks for input failed!!!\n====================\ntext\n====================')
    return total_time


async def make_requests(d, args):
    stt = time.time()
    latencies = await asyncio.gather(*[make_request(text) for text in d])
    total_time = time.time() - stt

    latency = statistics.mean(latencies)
    throughput = len(d) / total_time
    print(f'{len(d)} requests took %0.2f seconds, which is %0.2f requests/sec, with a latency of %0.2f ms' % (total_time, throughput, latency))
    return throughput, latency


# Benchmarking
print(f'Testing {args.num_examples} examples')
test_sentence = "word " * (args.seq_length - 4)
dummy_array = [test_sentence, ] * args.num_examples

loop = asyncio.get_event_loop()
loop.run_until_complete(make_requests(dummy_array, args))
loop.close()
