# AEM Security & Access Control

## Purpose
Implement comprehensive security configurations including user/group management, ACL policies, CSRF protection, SSL configuration, and security hardening for AEM environments.

## When to Use (Triggers)
- User mentions "permissions," "ACL," "access control," or "security"
- References to users, groups, rep:policy, or service users
- Questions about CSRF tokens, SSL, SAML SSO, or authentication
- Requests involving content access restrictions or permission testing
- File paths containing `/home/users/`, `/home/groups/`, or `rep:policy` nodes

## Core Capabilities
- Design group hierarchies and permission inheritance strategies
- Implement fine-grained ACL policies using CRX DE or repoinit scripts
- Configure service users for OSGi bundles and system operations
- Set up SAML/OAuth/IMS authentication integration
- Apply AEM security hardening checklist and dispatcher security rules

## Domain Knowledge Required
### Technical Foundation
- JCR access control model (allow, deny, glob restrictions, rep:ntNames)
- Oak security architecture: authentication, authorization, principal management
- Service user mapping (`org.apache.sling.serviceusermapping.impl.ServiceUserMapperImpl`)
- Apache Sling authentication handler chain

### AEM-Specific Context
- AEM built-in groups (administrators, content-authors, dam-users, workflow-editors)
- Closed User Groups (CUG) for publish-side access restriction
- Adobe IMS integration for AEM Cloud Service
- Dispatcher security: filter rules, URL fingerprinting, DOT restriction
- Crypto support and credential storage in AEM

## Implementation Approach
### Step 1: Security Architecture
Define the permission model aligned with organizational structure.
- Map business roles to AEM functional groups
- Design group hierarchy (base groups → role groups → project groups)
- Plan content path access matrix
- Identify service accounts needed for system operations

### Step 2: Group & User Configuration
Implement the permission structure via repoinit or packages.
- Create groups using Sling repoinit scripts (preferred for Cloud Service)
- Define group nesting and membership
- Configure group profiles with descriptions
- Set up LDAP/SAML sync for external identity providers

### Step 3: ACL Policy Definition
Apply granular permissions to content paths.
- Define allow/deny ACEs on content paths
- Use glob restrictions for pattern-based access (`*/jcr:content/metadata`)
- Apply `rep:ntNames` restrictions for node-type filtering
- Configure `rep:itemNames` for property-level access control

### Step 4: Service User Setup
Create system accounts for bundle operations.
- Define service users via repoinit scripts
- Map service users to bundles using ServiceUserMapper
- Grant minimum required permissions to service users
- Validate service user resource resolution works correctly

### Step 5: Security Hardening
Apply defense-in-depth security measures.
- Configure CSRF filter allowlisting
- Enable and configure Content Security Policy headers
- Set up SSL/TLS on all environments
- Disable unused servlets and endpoints
- Configure Referrer Filter for cross-origin protection

## Quality Checklist
- [ ] All content authors can only access their designated content trees
- [ ] Service users follow principle of least privilege
- [ ] No anonymous access to sensitive content on publish
- [ ] CSRF protection active on all mutation endpoints
- [ ] Dispatcher filters block direct access to sensitive paths
- [ ] Admin accounts use strong authentication (IMS/SAML)
- [ ] Permission changes are version-controlled via repoinit scripts
- [ ] Security audit logs capture access violations

## Related Skills
- aem-dispatcher-configuration (security filtering)
- aem-monitoring-alerting (security event monitoring)
- aem-custom-osgi-services (service user usage)

## Example Use Cases
1. **Multi-Tenant Content Platform:** Design permission model for 15 content teams with strict content isolation, shared asset library access, and cross-team review workflows.
2. **Extranet with CUG:** Implement closed user group on publish with SAML-based login, token-based session management, and automatic session timeout with re-authentication.
3. **Service Account Hardening:** Audit and remediate service user permissions, replacing broad admin-like accounts with scoped service users per bundle using repoinit scripts.

## Notes
- AEM Cloud Service requires repoinit scripts for all user/group/ACL provisioning — no package-based deployment
- Deny ACEs take precedence at the same path; more-specific path ACEs take precedence over parent paths
- Never grant `jcr:all` to service users — always grant minimum required privileges
- Test permission changes with the "Impersonate" feature before deploying to production
