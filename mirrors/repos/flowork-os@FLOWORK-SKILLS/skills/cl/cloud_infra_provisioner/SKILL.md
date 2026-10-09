---
name: cloud_infra_provisioner
description: Sovereign runbook for Terraform and OpenTofu infrastructure as code, immutable cloud state, modular provisioning, and zero-drift deployments
keywords: ["infrastructure as code", "terraform provisioner", "opentofu", "cloud infrastructure", "terraform state", "remote backend", "provider configuration", "terraform module", "variable validation", "cloud resource planning", "terraform plan", "immutable infrastructure", "cloud security posture", "state locking", "drift detection", "hcl syntax", "resource dependency", "cloud migration", "zero drift deploy", "cost optimization"]
---

# ⚙️ SKILL: CLOUD INFRA PROVISIONER (IAC)

## 1. Intent & Trigger Boundaries
- **Intent**: Deklarasi dan provisi infrastruktur komputasi awan (AWS, GCP, Azure, Cloudflare, Hetzner, DigitalOcean) menggunakan Terraform atau OpenTofu secara deterministik, modular, dan bebas drift.
- **Trigger**: Diminta merancang infrastruktur cloud, provisioning VM, VPC, database terkelola, CDN DNS, S3 buckets, atau menulis modul Terraform/OpenTofu HCL.
- **Boundaries**: Tidak mengurusi arsitektur kode internal aplikasi di level runtime container (gunakan `docker_container_deployer` atau `k8s_cluster_commander`). Fokus pada level lapisan infrastruktur cloud / IaaS / PaaS.

## 2. Standard Operating Procedures (SOP)
1. **State Isolation & Remote Backend**:
   - Selalu gunakan remote backend aman (misal S3 + DynamoDB state locking atau Terraform Cloud) untuk menyimpan file `.tfstate`.
   - Pisahkan state per environment (`environments/prod`, `environments/staging`) atau workspace untuk membatasi radius kehancuran.
2. **Modular HCL Scaffolding**:
   - Rancang arsitektur HCL terpecah: `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`.
   - Modul harus reusable dan terisolasi dengan validasi tipe input variabel (`validation` block).
   - Selalu kunci versi provider dan OpenTofu/Terraform binary di `versions.tf`.
3. **Execution Safety Pipeline**:
   - Eksekusi selalu melalui urutan baku: `fmt -check` -> `validate` -> `plan -out=tfplan` -> audit manusia/CI -> `apply tfplan`.
   - Dilarang menjalankan `apply -auto-approve` tanpa melihat output plan terlebih dahulu.
4. **Secrets & Tags Hygiene**:
   - Gunakan environment variables (`TF_VAR_*`) atau HashiCorp Vault / KMS untuk menginjeksi kredensial cloud.
   - Tetapkan tagging standar (Environment, Owner, Project, ManagedBy=Terraform) pada seluruh resource.

## 3. Strict Prohibitions & Edge Cases
- **PROHIBITION**: Dilarang commit berkas `.tfstate` lokal atau secret variables (`terraform.tfvars` berisi token) ke repository git.
- **PROHIBITION**: Dilarang melakukan modifikasi manual melalui cloud console web pada resource yang dikelola Terraform (mencegah drift).
- **EDGE CASE**: Terjadi state lock terhenti karena crash: identifikasi lock ID dan jalankan `force-unlock` hanya setelah verifikasi tidak ada apply lain yang aktif.

## 4. Verification & Exit Code 0 Proof
- Formatting check: `terraform fmt -check` menghasilkan exit code 0.
- Validasi struktur: `terraform validate` mengembalikan status "Success! The configuration is valid." dengan exit code 0.
- Perencanaan provisi: `terraform plan -detailed-exitcode` selesai tanpa kegagalan provider.
