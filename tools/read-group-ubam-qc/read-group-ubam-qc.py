#!/usr/bin/env python3

import os
import sys
import json
from argparse import ArgumentParser
import subprocess


def run_cmd(cmd):
  stdout, stderr, p, success = '', '', None, True
  try:
    p = subprocess.Popen([cmd],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True)
    stdout, stderr = p.communicate()
  except Exception as e:
    print('Execution failed: %s' % e, file=sys.stderr)
    success = False

  if p and p.returncode != 0:
    print('Execution failed, none zero code returned.', file=sys.stderr)
    success = False

  print(stdout.decode("utf-8"))
  print(stderr.decode("utf-8"), file=sys.stderr)

  if not success:
    sys.exit(p.returncode if p.returncode else 1)

  return stdout, stderr


def collect_ubam_info(ubam):
  cmd = "samtools view -H %s |grep '^@RG' | tr '\t' '\n' |grep '^ID:' | sed 's/ID://'" % ubam

  stdout, _ = run_cmd(cmd)
  read_group_id = stdout.decode("utf-8").strip()

  if not read_group_id:
    sys.exit('Error: unable to find read group ID in lane level BAM %s' % ubam)
  elif '\n' in read_group_id:
    sys.exit('Error: more than one read group ID found in lane level BAM %s' % ubam)

  ubam_info = {
    'read_group_id': read_group_id,
    'name': os.path.basename(ubam),
    'size': os.path.getsize(ubam)
  }

  with open("%s.ubam_info.json" % ubam, 'w') as f:
    f.write(json.dumps(ubam_info, indent=2))


def collect_metrics(ubam):
  metrics_file = "%s.quality_yield_metrics.txt" % ubam
  command = "java -jar /tools/picard.jar CollectQualityYieldMetrics I=%s O=%s" % (ubam, metrics_file)

  run_cmd(command)


def main():
  parser = ArgumentParser()
  parser.add_argument("-b", "--ubam", dest="ubam", help="Lane level unmapped BAM file", type=str)
  args = parser.parse_args()

  collect_ubam_info(args.ubam)

  collect_metrics(args.ubam)


if __name__ == '__main__':
  main()