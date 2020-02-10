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

 Author: Linda Xiang <linda.xiang@oicr.on.ca>
         Junjun Zhang <junjun.zhang@oicr.on.ca>
"""

import os
import sys
from argparse import ArgumentParser
import subprocess
from multiprocessing import cpu_count
import tarfile
import glob


def collect_metrics(args):
  # generate stats_args string
  stats_args = [
      '--reference', args.reference,
      '-@', str(args.cpus),
      '-r', args.reference,
      '--split', 'RG',
      '-P', os.path.join(os.getcwd(), os.path.basename(args.seq))
  ]

  try:
      cmd = ['samtools', 'stats'] + stats_args + [args.seq]
      p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
  except Exception as e:
      sys.exit("Error: %s. 'samtools stats' failed: %s\n" % (e, args.seq))

  with open(os.path.join(os.getcwd(), os.path.basename(args.seq)+".bamstat"), 'w') as f:
      f.write(p.stdout.decode('utf-8'))

  # make tar gzip ball of the *.bamstat files
  tarfile_name = os.path.basename(args.seq)+'.qc_metrics.tgz'
  with tarfile.open(tarfile_name, "w:gz") as tar:
      for statsfile in glob.glob(os.path.join(os.getcwd(), "*.bamstat")):
          tar.add(statsfile, arcname=os.path.basename(statsfile))

def main():
  parser = ArgumentParser()
  parser.add_argument("-s", "--seq", dest="seq", help="Aligned sequence file", type=str, required=True)
  parser.add_argument('-r', '--reference', dest='reference', type=str, help='reference fasta', required=True)
  parser.add_argument('-n', '--cpus', dest='cpus', type=int, help='number of cpu cores', default=cpu_count())

  args = parser.parse_args()

  collect_metrics(args)


if __name__ == '__main__':
  main()