#!/usr/bin/env cwl-runner

class: Workflow
cwlVersion: v1.1
id: calculate-contamination

requirements:
- class: StepInputExpressionRequirement
- class: ScatterFeatureRequirement

inputs:
    interval_file: File?
    jvm_mem: int?
    normal_seq_file:
      secondaryFiles:
        - .bai?
        - .crai?
      type: File
    ref_dict: File
    ref_fa:
      secondaryFiles:
        - .fai
        - ^.dict
      type: File
    scatter_count: int
    split_intervals_extra_args: string?
    tumour_seq_file:
      secondaryFiles:
        - .bai?
        - .crai?
      type: File
    variants_for_contamination:
      secondaryFiles:
        - .tbi
      type: File


outputs:
  contamination_table:
    type: File
    outputSource: calculate_contamination/contamination_table
  tumour_segmentation_table:
    type: File
    outputSource: calculate_contamination/segmentation_table

steps:

  split_intervals:
    run: https://raw.githubusercontent.com/icgc-argo/gatk-tools/gatk-split-intervals.4.1.3.0-1.0/tools/gatk-split-intervals/gatk-split-intervals.cwl
    in:
      jvm_mem: jvm_mem
      ref_fa: ref_fa
      intervals: interval_file
      scatter_count: scatter_count
      split_intervals_extra_args: split_intervals_extra_args
    out: [ interval_files ]

  get_normal_pileup_summaries:
    run: https://raw.githubusercontent.com/icgc-argo/gatk-tools/gatk-get-pileup-summaries.4.1.3.0-1.1/tools/gatk-get-pileup-summaries/gatk-get-pileup-summaries.cwl
    scatter: intervals
    in:
      jvm_mem: jvm_mem
      ref_fa: ref_fa
      seq_file: normal_seq_file
      variants: variants_for_contamination
      intervals: split_intervals/interval_files
      output_name: { default: 'normal_pileup_summary.tsv' }
    out: [ pileups_table ]

  get_tumour_pileup_summaries:
    run: https://raw.githubusercontent.com/icgc-argo/gatk-tools/gatk-get-pileup-summaries.4.1.3.0-1.1/tools/gatk-get-pileup-summaries/gatk-get-pileup-summaries.cwl
    scatter: intervals
    in:
      jvm_mem: jvm_mem
      ref_fa: ref_fa
      seq_file: tumour_seq_file
      variants: variants_for_contamination
      intervals: split_intervals/interval_files
      output_name: { default: 'tumour_pileup_summary.tsv' }
    out: [ pileups_table ]

  merge_normal_pileups:
    run: https://raw.githubusercontent.com/icgc-argo/gatk-tools/gatk-gather-pileup-summaries.4.1.3.0-1.0/tools/gatk-gather-pileup-summaries/gatk-gather-pileup-summaries.cwl
    in:
      jvm_mem: jvm_mem
      ref_dict: ref_dict
      input_pileup: get_normal_pileup_summaries/pileups_table
      output_name: { default: 'normal_pileup_merged.tsv' }
    out: [ merged_pileup ]

  merge_tumour_pileups:
    run: https://raw.githubusercontent.com/icgc-argo/gatk-tools/gatk-gather-pileup-summaries.4.1.3.0-1.0/tools/gatk-gather-pileup-summaries/gatk-gather-pileup-summaries.cwl
    in:
      jvm_mem: jvm_mem
      ref_dict: ref_dict
      input_pileup: get_tumour_pileup_summaries/pileups_table
      output_name: { default: 'tumour_pileup_merged.tsv' }
    out: [ merged_pileup ]

  calculate_contamination:
    run: https://raw.githubusercontent.com/icgc-argo/gatk-tools/gatk-calculate-contamination.4.1.3.0-1.0/tools/gatk-calculate-contamination/gatk-calculate-contamination.cwl
    in:
      jvm_mem: jvm_mem
      tumour_pileups: merge_tumour_pileups/merged_pileup
      normal_pileups: merge_normal_pileups/merged_pileup
      segmentation_output: { default: 'segments.table' }
      contamination_output: { default: 'contamination.table' }
    out: [ segmentation_table, contamination_table ]


