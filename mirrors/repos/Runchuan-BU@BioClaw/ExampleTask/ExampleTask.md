## BioClaw Demo Prompts (Mobile-Friendly)

This document contains 6 copy/paste prompts for a BioClaw WhatsApp demo.

Notes:
- Prompts that reference `/workspace/group/...` assume the file exists in the group workspace.
  On the host, that is typically `BioClaw/groups/<your-group-folder>/`.
- Markdown supports images. This file embeds the local screenshots `1.jpg` to `6.jpg` in this folder.

---

### 1) Workspace Triage (List + Next Steps)

Copy/paste:

```text
@Bioclaw In /workspace/group/4, list the files and recommend the best next analysis steps. Keep it short (max 8 bullets) and ask me 1 question to proceed.
```

![Demo 1](./1.jpg)

---

### 2) FastQC Quick Summary (With Images)

Copy/paste:

```text
@Bioclaw Make a quick QC summary from /workspace/group/reads_R1.fastq.gz and /workspace/group/reads_R2.fastq.gz (FastQC). Send me the key findings in bullets and also send the FastQC report image(s) to WhatsApp.
```

![Demo 2](./2.jpg)

---

### 3) BLAST Top Hits (Structured Output)

Copy/paste:

```text
@Bioclaw BLAST this sequence against nr (protein). Tell me the top 5 hits with species, % identity, e-value, and a one-line interpretation:
>query
MSTNPKPQRKTKRNTNRRPQDVKFPGG...
```

![Demo 3](./3.jpg)

---

### 4) Volcano Plot From CSV (With Image + Takeaway)

Copy/paste:

```text
@Bioclaw Create a simple volcano plot from /workspace/group/counts.csv (assume columns: gene, log2FC, pvalue). Use readable labels, export a PNG, and send the plot image to WhatsApp with a 2-sentence takeaway.
```

![Demo 4](./4.jpg)

---

### 5) Protein Structure Render (PDB 1UBQ)

Copy/paste:

```text
@Bioclaw Render the structure of PDB 1UBQ in rainbow colors, generate a high-resolution image, and send it to WhatsApp. Then give me 3 bullets describing what I'm looking at.
```

![Demo 5](./5.jpg)

---

### 6) PubMed Search (Recent Papers Summary)

Copy/paste:

```text
@Bioclaw Search PubMed for recent papers about ADHD published in high-impact journals and summarize the top three. For each paper: citation, why it matters, and 1 limitation.
```

![Demo 6](./6.jpg)
