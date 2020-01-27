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


def collect_metrics(args):
  # generate jvm string
  if not args.memory is None:
      jvm_args = '-Xmx'+args.memory+"g"
  else:
      jvm_args = ''

  # detect the format of input file
  if os.path.basename(args.seq).endswith(".bam"):
      cmd1 = (
          f'java {jvm_args} -jar /tools/picard.jar CollectMultipleMetrics I={args.seq} O=multiple_metrics R={args.reference} ')

  elif os.path.basename(args.seq).endswith(".cram"):
      cmd1 = (
          f'samtools view -b -T {args.reference} {args.seq} -o /dev/stdout | '
          f'java {jvm_args} -jar /tools/picard.jar CollectMultipleMetrics I=/dev/stdin O=multiple_metrics R={args.reference} ')

  else:
      sys.exit("Unknown alignment sequence format!")

  cmd2 = (
          f'ASSUME_SORTED=true '
          f'PROGRAM=null '
          f'PROGRAM=CollectBaseDistributionByCycle '
          f'PROGRAM=CollectAlignmentSummaryMetrics '
          f'PROGRAM=CollectInsertSizeMetrics '
          f'PROGRAM=MeanQualityByCycle '
          f'PROGRAM=QualityScoreDistribution '
          f'PROGRAM=CollectSequencingArtifactMetrics '
          f'PROGRAM=CollectQualityYieldMetrics '
          f'METRIC_ACCUMULATION_LEVEL=null '
          f'METRIC_ACCUMULATION_LEVEL=ALL_READS '
          f'METRIC_ACCUMULATION_LEVEL=SAMPLE '
          f'METRIC_ACCUMULATION_LEVEL=LIBRARY '
          f'METRIC_ACCUMULATION_LEVEL=READ_GROUP')


  run_cmd( cmd1+cmd2 )


def main():
  parser = ArgumentParser()
  parser.add_argument("-s", "--seq", dest="seq", help="Aligned sequence file", type=str)
  parser.add_argument('-r', '--reference', dest='reference',
                      type=str, help='reference fasta', required=True)
  parser.add_argument('-m', '--memory', dest='memory',
                      type=str, help='allocated process memory', default=None )

  args = parser.parse_args()

  collect_metrics(args)


if __name__ == '__main__':
  main()