#!/usr/bin/env nextflow

/*
 * Copyright (c) 2019-2020, Ontario Institute for Cancer Research (OICR).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

/*
 * author Junjun Zhang <junjun.zhang@oicr.on.ca>
 *        Linda Xiang <linda.xiang@oicr.on.ca>
 */

nextflow.preview.dsl=2
version = '0.1.0.0'

params.seq = ""
params.container_version = ""
params.ref_genome = ""


process alignedSeqQC {
  container "quay.io/icgc-argo/aligned-seq-qc:aligned-seq-qc.${params.container_version ?: version}"

  input:
    path seq
    path ref_genome

  output:
    path "multiple_metrics.*", emit: metrics

  script:
    jvm_mem_GB = task.memory ? "-m " + (task.memory.toGiga()-1) : ""

    """
    aligned-seq-qc.py -s ${seq} \
                      -r ${ref_genome} \
                      ${jvm_mem_GB}
    """
}