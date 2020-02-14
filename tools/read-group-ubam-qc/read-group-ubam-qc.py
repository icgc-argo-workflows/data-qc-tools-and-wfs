#!/usr/bin/env python3

"""
 Copyright (c) 2019-2020, Ontario Institute for Cancer Research (OICR).

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.

 Author: Junjun Zhang <junjun.zhang@oicr.on.ca>
"""

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
  cmd = "samtools view -H %s |grep '^@RG' | tr '\t' '\n' |grep '^ID:' | sed 's/ID://g'" % ubam

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


def collect_metrics(ubam, mem=None):
  metrics_file = "%s.quality_yield_metrics.txt" % ubam
  jvm_Xmx = "-Xmx%sM" % mem if mem else ""
  command = "java %s -jar /tools/picard.jar CollectQualityYieldMetrics " % jvm_Xmx+ \
            "I=%s O=%s ASSUME_SORTED=false VALIDATION_STRINGENCY=LENIENT" % (ubam, metrics_file)

  run_cmd(command)


def main():
  parser = ArgumentParser()
  parser.add_argument("-b", "--ubam", dest="ubam", help="Lane level unmapped BAM file", type=str)
  parser.add_argument("-m", "--mem", dest="mem", help="Maximal allocated memory in MB", type=int)
  args = parser.parse_args()

  collect_ubam_info(args.ubam)

  collect_metrics(args.ubam, args.mem)

  cmd = 'tar czf %s.ubam_qc_metrics.tgz *.quality_yield_metrics.txt *.ubam_info.json' % args.ubam
  run_cmd(cmd)


if __name__ == '__main__':
  main()
