---
type: skill
lifecycle: stable
inheritance: inheritable
name: remediate-pfx-certificates
description: Skill helps user to remove checked-in certificates from source code in case of exposed secrets
tier: standard
applyTo: '**/*remediate*,**/*pfx*,**/*certificates*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

Look for exposed secrets in current repository. You may find tokens, connection string, certificates (pfx files). Remove the checked in certificate files from the repository and create a pull request with this change.

# PFX (Personal Information Exchange) Found in Source Code

**Why did I get this alert?**

An Azure DevOps Git repository owned by your service has a checked-in certificate file (.pfx) that includes the certificate’s private key. You must act assuming this certificate has been compromised and must no longer be trusted by your service. This compromised certificate may be used by your service for one of many different purposes:

- Confidential client authentication for Entra applications  
- Server TLS authentication  
- Client TLS authentication  
- Data encryption  

The security team cannot tell how your service is using the compromised certificate and was issued. You must investigate and determine the appropriate remediation steps for your service.

>[!NOTE]
>For non-production resources, please move to NPE tenant. Refer to this [documentation](https://eng.ms/docs/products/torus/npetenant) for more information.

**How long do I have to remediate the action items?**

- This is part of Security Sprint Wave 1 – [ES 8](https://microsoft.sharepoint.com/sites/ExperiencesandDevicesED-SecuritySprintApril-July/SitePages/E&D-Security-Wave---Engineering%20Systems%20Standardization%20&%20Hardening.aspx). You must start working on this issue immediately if it is a live secret and for the rest you must complete it by the end of the sprint 7/21. Follow Safe Deployment and test practices to remediate the issue.

## Identify Impacted Services, Certificates, and PFX Files

Each alert represents a unique place where that certificate exists in a repo and has a thumbprint column that is a unique identifier for a certificate. Other columns in the alert contain important metadata about the certificate, like Issuer and Subject.
Each certificate thumbprint may have many rows in that table since some certificates have been copied multiple times within a repo or across multiple repos.
At this point, all certificates being flagged for service teams are present in the latest version of the default branch in at least one repo. Therefore, if you need the certificate content, you can start by looking at the repo and path information.

## Key Terms in this document

- Invalidating the certificate means updating your code or configuration to no longer trust the certificate.  
- Revoking the certificate means contacting the certificate authority (CA) to add the certificate's serial number to a revocation list.

## Remediation Steps  

**Note**: This S360 KPI relies on Cloudmine's CodeAsData Kusto cluster, hence the latency to reflect the changes can take about a week (after team has mitigated the PFX file in source code, it can take about a week to automatically remove the action item).



There are three potential paths for you to follow:

- Cert was issued via OneCert (e.g., AME CA, MSPKI, DigiCert, or accepted list).
- Cert is self-signed or issued by any CA not on the accepted list.
- General guidance for scenarios not covered in #1 or #2.

### Scenario #1: If your cert was issued via OneCert (e.g., AME CA, MSPKI (Microsoft PKI), DigiCert, or accepted list)

The following applies to certificates used for Server TLS or Client Authentication. You need to rotate the cert immediately by following these steps:

1. Rotate the Certificate in Key Vault or dSMS:

    - Certificate in Key Vault: [About Azure Key Vault certificate renewal](https://learn.microsoft.com/en-us/azure/key-vault/certificates/overview-renew-certificate?tabs=azure-cli)  
    - Certificate in dSMS: [Chained Certificates - Rollover and Update](https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/key-vault-dsms/dsms/secrettypes/managedsecrets/chainedcertificates/chainedcertificateupdaterollover)

2. Update Service with Rotated Certificate and Invalidate the Old Certificate: Update your service to use the rotated certificate, verify there is no usage of the old certificate, verify changes for your end-to-end scenario works, and deploy using SDP.

    - Certificate Pinning: If the certificate was being used for client authentication and it was authorized through certificate pinning, then also update the pin to be to the new certificate.
    - SNI: If the certificate was authorized through subject name and issuer authentication (“SNI”), or was used for server TLS, then you do not need to take additional steps and the certificate will be revoked in step 3.  

3. Revoke certificate: If you need OneCert to revoke your certificate, open an IcM Incident for the OneCert service’s Incident Manager team to revoke the certificate.
4. Delete Old PFX from Source: Remove the old PFX file from source. There is no need to purge commit history because the cert is already compromised.

### Scenario #2: If your cert is self-signed or issued by any CA not on the accepted list

The following applies to certificates used for Server TLS or Client Authentication. You must start using OneCert immediately by following these steps:

1. Create a Key Vault: If you do not have one in the same tenant boundary as your service (e.g., AME), create a key vault.

- [Quickstart - Create an Azure Key Vault with the Azure portal](https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal)

2. Register a New Domain in OneCert: Your domain registration environment (e.g., Public Cloud) and tenant (e.g., AME) must match your key vault environment and tenant.  

- [Registering a Domain in OneCert](https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/onecert-customer-guide/onecert/docs/registering-a-domain-in-onecert)

3. Create a New Certificate in Key Vault: Issue a new certificate and store in key vault by following these steps:  [Create a Certificate Using Key Vault](https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/onecert-customer-guide/onecert/docs/requesting-a-onecert-certificate-with-keyvault)
4. Update Service with Rotated Certificate and Invalidate the Old Certificate: Update your service to use the new certificate (using key vault not checked into source code), verify there is no usage of the old certificate, verify changes for your end-to-end scenario works, and deploy using SDP. If the old certificate was issued by a certificate authority, follow its instructions to revoke it. Note that self-signed certs cannot be revoked.
5. Revoke certificate: If it is a 3rd party issued CA, they revoke the certificate by contacting your provider. Self-Signed certs can skip this step as its N.A.
6. Delete old PFX from Source: Remove the old PFX file from source. There is no need to purge commit history because the cert is already compromised 

>[!NOTE]
>See [ FAQ](https://eng.ms/docs/microsoft-security/digital-security-and-resilience/m365-security-engineering/security-services/o365-service-auth-torus/secrets-prioritization/horizon-1/faq) Question #6 if your team can confirm that the cert is being used for benign testing purposes with no production impact.

### Scenario #3: The following remediation steps are general guidance.

1. Review the compromised certificate and determine how it is used by your service. You will need to engage the owners and experts of your service to analyze your code and gain this understanding.  
2. Rotate the compromised certificate: If the compromised certificate is used in production by your service, you must rotate the compromised certificate.You must generate a new certificate and securely store it. Do not store the new certificate in a code repo. You must store the certificate in an approved secrets store like KeyVault or dSMS and your service must access the certificate using this store. For guidance on approved certificate storage see [here](https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/key-vault-dsms/secretstoredecision) and [here](https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/key-vault-dsms/certandsecretmngmt/overview).  

You must modify your service to use the new certificate. You must follow safe deployment practices to deploy necessary changes to your service to use the new certificate.

#### Note: If the compromised certificate was used for encrypting production data stored in your service, you must design a plan to re-encrypt the data with the new certificate while ensuring continuity of service.  

Invalidate the certificate: If the compromised certificate is used in production by your service, you must invalidate the certificate so that it is no longer accepted. The mechanism to invalidate the certificate will vary depending on what your service uses this certificate for and how the certificate is issued.

For general guidance on certificate handling, see [here](https://eng.ms/docs/products/onecert-certificates-key-vault-and-dsms/key-vault-dsms/autorotationandecr/overviewcertificatemanagement).

### FAQs (Frequently Asked Questions)  

**What is a PFX File?**

A PFX (Personal Information Exchange) file is used to store cryptographic objects such as private keys, public keys, and certificates, along with their associated chain of trust. PFX files are typically password-protected for security purposes. They typically include:

1. Private Key: The private key is a sensitive cryptographic key used for decrypting data encrypted with the corresponding public key. It is crucial to keep the private key secure and protected from unauthorized access.  
2. Public Key: The public key is derived from the private key and is used for encrypting data that can only be decrypted by the corresponding private key. Public keys are often included in certificates for use in encryption and digital signatures.  
3. Certificate: Certificates contain information such as the entity's identity, public key, expiration date, and the digital signature of the issuing authority  
4. Chain of Trust: The chain of trust refers to the hierarchy of certificates that establishes the authenticity and validity of a certificate. It includes the certificate itself, intermediate certificates (if any), and the root certificate issued by a trusted certificate authority (CA).  
5. Password Protection: PFX files are often password-protected to prevent unauthorized access. The password is used to encrypt the private key and other sensitive information stored in the file.  

**How do I handle expired certs used for encryption of data at rest?**

If your expired cert is used for encryption of data at rest, the encrypted data should be considered at risk of compromise. You need to re-encrypt your data with a new certificate.

**Have more questions?**

Ask [ES Chat](https://aka.ms/eschat-teams) (AI Based Support Assistant) before reaching out to us. Engineering System (ES) Chat, our AI-based support assistant for Microsoft’s engineering systems. It provides personalized support leveraging documentation (EngHub, StackOverflow @ MS, etc) and Skills codified by many teams across 1ES to enhance productivity, streamline workflows, set up assets, handle onboarding, and diagnose problems.