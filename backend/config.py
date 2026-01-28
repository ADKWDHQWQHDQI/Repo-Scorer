"""Configuration for repository assessment questions and scoring"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass


class RepositoryTool(str, Enum):
    """Supported repository tools"""
    GITHUB = "github"
    GITLAB = "gitlab"
    AZURE_DEVOPS = "azure_devops"
    BITBUCKET = "bitbucket"


class CICDPlatform(str, Enum):
    """Supported CI/CD platforms"""
    GITHUB_ACTIONS = "github_actions"
    AZURE_PIPELINES = "azure_pipelines"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    CIRCLECI = "circleci"


class DeploymentPlatform(str, Enum):
    """Supported deployment platforms"""
    AZURE = "azure"
    AWS = "aws"
    GCP = "gcp"
    ON_PREMISE = "on_premise"
    KUBERNETES = "kubernetes"


@dataclass
class Question:
    """Individual question with manually assigned importance weight"""
    id: str
    text: str
    max_score: float
    importance: float  # Manual importance score (1-10 scale) - higher means more critical
    pillar: str  # Pillar category this question belongs to
    description: str = ""  # Two-line explanation of how the feature works
    doc_url: str = ""  # Official documentation URL for the feature


@dataclass
class Pillar:
    """Scoring pillar with questions"""
    name: str
    total_weight: float
    questions: List[Question]


# GitHub Questions - Top 5 Most Important (sorted by importance)
# Each tuple is (question_text, importance_score, pillar_category, description, doc_url)
# Importance scale: 1-10 (1=low, 10=critical)
GITHUB_QUESTIONS = [
    (
        "Is MFA (Multi-Factor Authentication) enabled for all organization members?",
        8.0,
        "governance",
        "Multi-Factor Authentication adds an extra layer of security by requiring users to provide two or more verification factors to access their GitHub account. This helps prevent unauthorized access even if passwords are compromised.",
        "https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-two-factor-authentication-for-your-organization/requiring-two-factor-authentication-in-your-organization"
    ),
    (
        "Are secrets prevented from being committed using GitHub secret scanning?",
        8.0,
        "security",
        "Secret scanning automatically detects and alerts you when secrets like API keys, tokens, or passwords are accidentally committed to your repository. This prevents credential exposure and potential security breaches.",
        "https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning"
    ),
    (
        "Are security alerts (Dependabot, CodeQL) actively monitored and acted upon with defined SLAs?",
        8.0,
        "security",
        "Security alerts notify you about vulnerabilities in your dependencies and code through Dependabot and CodeQL analysis. Establishing SLAs ensures timely response and remediation of security issues.",
        "https://docs.github.com/en/code-security/security-advisories/working-with-repository-security-advisories/about-repository-security-advisories"
    ),
    (
        "Is branch protection enforced (mandatory PRs, minimum reviewers, status checks)?",
        8.0,
        "code_review",
        "Branch protection rules enforce workflows like requiring pull request reviews and passing status checks before merging code. This ensures code quality and prevents direct commits to critical branches.",
        "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches"
    ),
    (
        "Are repository visibility policies (public/internal/private) clearly defined and enforced?",
        7.0,
        "governance",
        "Repository visibility policies control who can access your code repositories within your organization. Clear policies help maintain security by ensuring sensitive code remains private while appropriate projects can be shared.",
        "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility"
    ),
]

# GitLab Questions - Top 5 Most Important (sorted by importance)
# Each tuple is (question_text, importance_score, pillar_category, description, doc_url)
# Importance scale: 1-10 (1=low, 10=critical)
GITLAB_QUESTIONS = [
    (
        "Is two-factor authentication (2FA) enabled for all group members?",
        8.0,
        "governance",
        "Two-factor authentication requires users to provide a second form of verification beyond their password, such as a mobile authenticator code. Enforcing 2FA across all group members significantly reduces the risk of account compromise and unauthorized access.",
        "https://docs.gitlab.com/ee/security/two_factor_authentication.html"
    ),
    (
        "Are push rules configured to prevent secrets, large files, or invalid commits?",
        8.0,
        "security",
        "Push rules allow you to enforce commit standards by rejecting commits that contain secrets, exceed file size limits, or don't meet naming conventions. This proactive approach prevents security issues and repository bloat before code enters your branches.",
        "https://docs.gitlab.com/ee/user/project/repository/push_rules.html"
    ),
    (
        "Are security scanning results (SAST, DAST, dependency scanning) reviewed before code promotion?",
        8.0,
        "security",
        "GitLab's security scanners automatically detect vulnerabilities in your code, dependencies, and running applications through SAST, DAST, and dependency scanning. Reviewing these results before merging ensures security issues are addressed early in the development cycle.",
        "https://docs.gitlab.com/ee/user/application_security/"
    ),
    (
        "Is merge request approval rules enforced based on branch and code area?",
        8.0,
        "code_review",
        "Merge request approval rules define which users or groups must approve changes before they can be merged, optionally scoped to specific branches or code areas. This ensures appropriate oversight and maintains code quality standards.",
        "https://docs.gitlab.com/ee/user/project/merge_requests/approvals/rules.html"
    ),
    (
        "Are protected branches configured with restricted push and merge permissions?",
        8.0,
        "code_review",
        "Protected branches restrict who can push commits directly or merge changes into important branches like main or production. This prevents accidental or unauthorized modifications to your critical codebase.",
        "https://docs.gitlab.com/user/project/repository/branches/protected/#push-and-merge-permissions"
    ),
]

# Azure DevOps Questions - Top 5 Most Important (sorted by importance)
# Each tuple is (question_text, importance_score, pillar_category, description, doc_url)
# Importance scale: 1-10 (1=low, 10=critical)
AZURE_DEVOPS_QUESTIONS = [
    (
        "Is multi-factor authentication (MFA) enabled for all users?",
        8.0,
        "governance",
        "Multi-factor authentication adds an additional security layer by requiring users to verify their identity through a second method beyond passwords. Azure DevOps integrates with Azure AD conditional access policies to enforce MFA organization-wide.",
        "https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/change-application-access-policies"
    ),
    (
        "Are service hooks or policies used to prevent secret leakage?",
        8.0,
        "security",
        "Service hooks and policies can trigger automated checks before code is committed or merged, scanning for exposed credentials and secrets. This helps prevent sensitive information from entering your repository and reduces security risks.",
        "https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies"
    ),
    (
        "Is credential scanning enabled to detect secrets in code?",
        8.0,
        "security",
        "Credential scanning automatically analyzes commits for exposed secrets like API keys, tokens, and passwords in your source code. When detected, it alerts your team immediately to prevent credential exposure and potential breaches.",
        "https://learn.microsoft.com/en-us/azure/devops/repos/security/github-advanced-security-code-scanning"
    ),
    (
        "Are branch policies enforced (minimum reviewers, build validation, comment resolution)?",
        8.0,
        "code_review",
        "Branch policies enforce quality gates by requiring pull request reviews, successful builds, and resolved comments before merging. This maintains code quality and prevents incomplete or untested changes from reaching protected branches.",
        "https://learn.microsoft.com/en-us/azure/devops/repos/git/branch-policies-overview"
    ),
    (
        "Are repository permissions managed using Azure AD groups with proper RBAC?",
        7.0,
        "governance",
        "Managing permissions through Azure Active Directory groups with Role-Based Access Control provides centralized, scalable access management. This ensures users have appropriate permissions based on their role while simplifying administration.",
        "https://learn.microsoft.com/en-us/azure/devops/organizations/security/about-permissions"
    ),
]

# Bitbucket Questions - Top 5 Most Important (sorted by importance)
# Each tuple is (question_text, importance_score, pillar_category, description, doc_url)
# Importance scale: 1-10 (1=low, 10=critical)
BITBUCKET_QUESTIONS = [
    (
        "Is two-step verification enabled for all workspace members?",
        8.0,
        "governance",
        "Two-step verification adds a second layer of security by requiring workspace members to confirm their identity through an authenticator app or SMS. Enforcing this reduces the risk of unauthorized access even when passwords are compromised.",
        "https://support.atlassian.com/bitbucket-cloud/docs/two-step-verification/"
    ),
    (
        "Are merge checks configured to prevent secrets from being committed?",
        8.0,
        "security",
        "Merge checks automatically scan pull requests for exposed secrets and credentials before allowing them to be merged. This proactive detection prevents sensitive information from entering your repository and reduces security vulnerabilities.",
        "https://support.atlassian.com/bitbucket-cloud/docs/configure-merge-checks-for-a-pull-request/"
    ),
    (
        "Are branch restrictions enforced (mandatory PRs, minimum approvers)?",
        8.0,
        "code_review",
        "Branch restrictions prevent direct commits to important branches and require pull requests with a minimum number of approvals before merging. This ensures code review processes are followed and maintains code quality standards.",
        "https://support.atlassian.com/bitbucket-cloud/docs/use-branch-permissions/"
    ),
    (
        "Is SAML/SSO authentication enforced for workspace access?",
        7.0,
        "governance",
        "SAML single sign-on provides centralized authentication through your organization's identity provider, simplifying access management. Enforcing SSO ensures consistent security policies and enables better audit trails across your workspace.",
        "https://support.atlassian.com/bitbucket-cloud/docs/configure-saml-sso-with-bitbucket-cloud/"
    ),
    (
        "Are security vulnerabilities in dependencies tracked and remediated with SLAs?",
        7.0,
        "security",
        "Bitbucket's security features help identify vulnerable dependencies in your projects through automated scanning. Establishing SLAs ensures security issues are prioritized and addressed promptly to reduce exposure risk.",
        "https://support.atlassian.com/bitbucket-cloud/docs/bitbucket-cloud-security/"
    ),
]


# ========================================
# CI/CD PLATFORM QUESTIONS (5 questions each)
# ========================================

# GitHub Actions Questions
GITHUB_ACTIONS_QUESTIONS = [
    (
        "Are GitHub Actions workflows triggered only from protected branches?",
        8.0,
        "cicd_security",
        "Restricting workflow triggers to protected branches prevents unauthorized or malicious code from executing in your CI/CD pipelines. This ensures only reviewed and approved code can trigger automated deployments and sensitive operations.",
        "https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows"
    ),
    (
        "Are workflow permissions set to least privilege (minimum required scopes)?",
        7.0,
        "cicd_security",
        "Configuring workflows with minimal permissions limits the potential damage if a workflow is compromised. By granting only the necessary token scopes, you reduce the attack surface and protect your repository resources.",
        "https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token"
    ),
    (
        "Are secrets stored securely using GitHub Secrets or environment-specific secrets?",
        8.0,
        "cicd_security",
        "GitHub Secrets provides encrypted storage for sensitive values like API keys and credentials used in workflows. Environment-specific secrets add another layer by restricting access based on deployment environments, preventing unauthorized use.",
        "https://docs.github.com/en/actions/security-guides/encrypted-secrets"
    ),
    (
        "Are third-party GitHub Actions pinned to specific commit SHAs instead of tags?",
        6.0,
        "cicd_governance",
        "Pinning actions to commit SHAs ensures your workflows use exact, immutable versions of third-party code. Tags can be moved or deleted, but commit SHAs remain fixed, protecting against supply chain attacks and unexpected changes.",
        "https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions#using-third-party-actions"
    ),
    (
        "Are required status checks configured to block merges on failing workflows?",
        7.0,
        "cicd_quality",
        "Required status checks prevent code from being merged if critical CI checks fail, such as tests or security scans. This maintains code quality by ensuring all automated validations pass before changes reach protected branches.",
        "https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches#require-status-checks-before-merging"
    ),
]

# Azure Pipelines Questions
AZURE_PIPELINES_QUESTIONS = [
    (
        "Are Azure Key Vault integrations used for secret management instead of pipeline variables?",
        8.0,
        "cicd_security",
        "Azure Key Vault provides centralized, secure storage for secrets with access controls, auditing, and encryption. Using Key Vault instead of plain pipeline variables prevents credential exposure and enables better secret lifecycle management.",
        "https://learn.microsoft.com/en-us/azure/devops/pipelines/release/azure-key-vault"
    ),
    (
        "Are pipeline permissions restricted using Azure AD groups and service connections?",
        7.0,
        "cicd_governance",
        "Managing pipeline access through Azure AD groups and service connections provides granular control over who can run, edit, or view pipelines. This centralized approach simplifies permission management and enhances security through role-based access.",
        "https://learn.microsoft.com/en-us/azure/devops/pipelines/policies/permissions"
    ),
    (
        "Are deployment approvals and gates configured for production environments?",
        7.0,
        "cicd_quality",
        "Approvals and gates add manual or automated checkpoints before deploying to production, allowing stakeholders to verify changes. This prevents unauthorized or untested code from reaching critical environments and enables controlled release processes.",
        "https://learn.microsoft.com/en-us/azure/devops/pipelines/release/approvals/approvals"
    ),
    (
        "Are agent pools secured and isolated per environment (dev/staging/prod)?",
        6.0,
        "cicd_security",
        "Isolating agent pools per environment prevents cross-contamination between development, staging, and production workloads. Dedicated agents with environment-specific configurations and permissions reduce security risks and ensure consistent deployments.",
        "https://learn.microsoft.com/en-us/azure/devops/pipelines/agents/pools-queues"
    ),
    (
        "Are pipeline audit logs monitored for unauthorized changes or executions?",
        6.0,
        "cicd_governance",
        "Pipeline audit logs track all changes, executions, and access events within your CI/CD infrastructure. Regular monitoring of these logs helps detect suspicious activity, unauthorized modifications, and compliance violations early.",
        "https://learn.microsoft.com/en-us/azure/devops/organizations/audit/azure-devops-auditing"
    ),
]

# GitLab CI Questions
GITLAB_CI_QUESTIONS = [
    (
        "Are CI/CD variables marked as 'protected' and 'masked' to prevent exposure?",
        8.0,
        "cicd_security",
        "Protected variables are only available to pipelines running on protected branches, while masked variables are hidden in job logs. These features prevent sensitive credentials from being exposed in logs or used by unauthorized pipeline runs.",
        "https://docs.gitlab.com/ee/ci/variables/#protected-cicd-variables"
    ),
    (
        "Are runners properly tagged and restricted to specific projects or groups?",
        7.0,
        "cicd_governance",
        "Tagging runners and restricting their availability ensures jobs run on appropriate infrastructure with proper security controls. This prevents resource abuse, maintains environment isolation, and ensures compliance with security policies.",
        "https://docs.gitlab.com/ee/ci/runners/configure_runners.html#use-tags-to-control-which-jobs-a-runner-can-run"
    ),
    (
        "Are deployment jobs configured with manual approval for production environments?",
        7.0,
        "cicd_quality",
        "Manual deployment approvals require human intervention before deploying to production, providing a final verification step. This prevents automated deployments of potentially problematic changes and enables controlled, deliberate releases.",
        "https://docs.gitlab.com/ee/ci/environments/deployment_approvals.html"
    ),
    (
        "Are security scanning jobs (SAST, DAST, dependency scanning) part of the CI pipeline?",
        7.0,
        "cicd_security",
        "Integrating security scanning into CI pipelines automatically detects vulnerabilities in code, dependencies, and running applications. This shift-left approach identifies security issues early when they're cheaper and easier to fix.",
        "https://docs.gitlab.com/ee/user/application_security/"
    ),
    (
        "Are pipeline artifacts set with appropriate expiration policies?",
        5.0,
        "cicd_governance",
        "Setting artifact expiration policies automatically removes old build artifacts after a defined period, preventing storage bloat. This helps manage costs while retaining artifacts for debugging and compliance requirements when needed.",
        "https://docs.gitlab.com/ee/ci/yaml/index.html#artifactsexpire_in"
    ),
]

# Jenkins Questions
JENKINS_QUESTIONS = [
    (
        "Are Jenkins credentials stored in credential managers (not hardcoded in pipelines)?",
        8.0,
        "cicd_security",
        "Jenkins Credentials plugin provides secure storage for sensitive information with encryption at rest and access controls. Storing credentials centrally rather than hardcoding them prevents exposure in pipeline code and version control systems.",
        "https://www.jenkins.io/doc/book/using/using-credentials/"
    ),
    (
        "Are agent nodes secured with proper authentication and authorization?",
        7.0,
        "cicd_security",
        "Securing agent nodes with authentication and authorization prevents unauthorized systems from connecting to your Jenkins controller. This protects your CI/CD infrastructure from compromised or malicious agents that could execute arbitrary code.",
        "https://www.jenkins.io/doc/book/security/controller-isolation/"
    ),
    (
        "Are pipeline approvals enabled before deploying to production?",
        7.0,
        "cicd_quality",
        "Input steps and approval gates in Jenkins pipelines require manual confirmation before proceeding with production deployments. This human checkpoint ensures changes are intentionally released and provides accountability for production modifications.",
        "https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/"
    ),
    (
        "Are Jenkins plugins regularly updated and security-scanned for vulnerabilities?",
        6.0,
        "cicd_governance",
        "Keeping Jenkins plugins updated patches known vulnerabilities and ensures compatibility with the latest Jenkins features. Regular security scanning identifies vulnerable plugins before they can be exploited, maintaining your CI/CD security posture.",
        "https://www.jenkins.io/doc/book/managing/plugins/"
    ),
    (
        "Are build artifacts stored securely with access controls and retention policies?",
        6.0,
        "cicd_governance",
        "Implementing access controls on build artifacts prevents unauthorized access to compiled code and build outputs. Retention policies automatically clean up old artifacts, balancing storage costs with compliance and debugging needs.",
        "https://www.jenkins.io/doc/book/using/artifacts/"
    ),
]

# CircleCI Questions
CIRCLECI_QUESTIONS = [
    (
        "Are environment variables configured as secrets in CircleCI project settings?",
        8.0,
        "cicd_security",
        "CircleCI encrypts environment variables configured as secrets and masks them in build logs, preventing credential exposure. Storing sensitive values like API keys and passwords as secrets protects them from unauthorized access and accidental disclosure.",
        "https://circleci.com/docs/env-vars/#setting-an-environment-variable-in-a-project"
    ),
    (
        "Are restricted contexts used to limit access to sensitive credentials?",
        7.0,
        "cicd_security",
        "Contexts in CircleCI group environment variables and restrict their use to specific security groups or projects. This granular access control ensures sensitive credentials are only available to authorized workflows and teams.",
        "https://circleci.com/docs/contexts/"
    ),
    (
        "Are approval jobs configured for production deployments?",
        7.0,
        "cicd_quality",
        "Approval jobs pause workflow execution until a team member manually approves continuation, typically before production deployments. This manual gate provides oversight and ensures deployments happen intentionally with proper authorization.",
        "https://circleci.com/docs/workflows/#holding-a-workflow-for-a-manual-approval"
    ),
    (
        "Are orbs (third-party integrations) from trusted sources and regularly reviewed?",
        6.0,
        "cicd_governance",
        "CircleCI orbs are reusable packages of configuration that can introduce third-party code into your pipelines. Using orbs only from trusted sources and reviewing them regularly helps prevent supply chain attacks and ensures security standards are maintained.",
        "https://circleci.com/docs/orb-intro/"
    ),
    (
        "Are build artifacts stored with proper access controls and retention limits?",
        6.0,
        "cicd_governance",
        "Setting retention limits on artifacts automatically removes old builds after a specified period, managing storage costs. Combined with access controls, this ensures build outputs are protected while maintaining only necessary historical data.",
        "https://circleci.com/docs/artifacts/"
    ),
]


# ========================================
# DEPLOYMENT PLATFORM QUESTIONS (5 questions each)
# ========================================

# Azure Deployment Questions
AZURE_DEPLOYMENT_QUESTIONS = [
    (
        "Are Azure resources deployed using Infrastructure as Code (Bicep, Terraform, ARM)?",
        7.0,
        "deployment_automation",
        "Infrastructure as Code enables version-controlled, repeatable deployments of Azure resources through declarative templates. Using tools like Bicep, Terraform, or ARM templates ensures consistency across environments and enables automated, auditable infrastructure changes.",
        "https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview"
    ),
    (
        "Are Azure Key Vault and Managed Identities used for secrets management?",
        8.0,
        "deployment_security",
        "Azure Key Vault securely stores secrets, keys, and certificates with access controls and audit logging. Managed Identities eliminate the need for credentials in code by automatically handling Azure service authentication, reducing credential exposure risks.",
        "https://learn.microsoft.com/en-us/azure/key-vault/general/overview"
    ),
    (
        "Are Azure Monitor and Application Insights configured for logging and alerting?",
        7.0,
        "deployment_monitoring",
        "Azure Monitor collects and analyzes telemetry from your applications and infrastructure, while Application Insights provides detailed application performance monitoring. Together they enable proactive issue detection through comprehensive logging and intelligent alerting.",
        "https://learn.microsoft.com/en-us/azure/azure-monitor/overview"
    ),
    (
        "Are Azure Policy and RBAC enforced to control resource access and compliance?",
        7.0,
        "deployment_security",
        "Azure Policy enforces organizational standards and compliance requirements by auditing and restricting resource configurations. Combined with Role-Based Access Control (RBAC), these features ensure users have appropriate permissions and resources comply with security policies.",
        "https://learn.microsoft.com/en-us/azure/governance/policy/overview"
    ),
    (
        "Are disaster recovery and backup strategies implemented for critical resources?",
        6.0,
        "deployment_reliability",
        "Disaster recovery plans and automated backups protect your critical Azure resources from data loss and service disruptions. Implementing strategies like Azure Site Recovery and backup policies ensures business continuity and enables rapid recovery from failures.",
        "https://learn.microsoft.com/en-us/azure/backup/backup-overview"
    ),
]

# AWS Deployment Questions
AWS_DEPLOYMENT_QUESTIONS = [
    (
        "Are AWS resources deployed using Infrastructure as Code (CloudFormation, Terraform, CDK)?",
        7.0,
        "deployment_automation",
        "Infrastructure as Code tools like CloudFormation, Terraform, and CDK allow you to define AWS resources in version-controlled templates. This approach ensures consistent, repeatable deployments across environments while enabling automated infrastructure management and change tracking.",
        "https://docs.aws.amazon.com/cloudformation/"
    ),
    (
        "Are AWS Secrets Manager and IAM roles used for secure credential management?",
        8.0,
        "deployment_security",
        "AWS Secrets Manager securely stores and rotates database credentials, API keys, and other secrets with automatic rotation capabilities. IAM roles provide temporary security credentials, eliminating the need to embed long-term credentials in your applications.",
        "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html"
    ),
    (
        "Are CloudWatch logs, metrics, and alarms configured for monitoring and alerting?",
        7.0,
        "deployment_monitoring",
        "Amazon CloudWatch collects and tracks metrics, monitors log files, and sets alarms for your AWS resources and applications. This comprehensive monitoring enables you to detect anomalies, optimize performance, and respond quickly to operational issues.",
        "https://docs.aws.amazon.com/cloudwatch/"
    ),
    (
        "Are IAM policies enforced with least privilege and multi-factor authentication (MFA)?",
        7.0,
        "deployment_security",
        "Implementing least privilege IAM policies grants users and services only the minimum permissions needed to perform their tasks. Requiring MFA adds an additional security layer for sensitive operations, significantly reducing the risk of unauthorized access.",
        "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html"
    ),
    (
        "Are automated backups and disaster recovery plans configured for critical services?",
        6.0,
        "deployment_reliability",
        "AWS backup solutions like AWS Backup and service-specific features automate data protection across your AWS resources. Combined with disaster recovery planning using services like AWS Backup and cross-region replication, this ensures business continuity and data resilience.",
        "https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html"
    ),
]

# GCP Deployment Questions
GCP_DEPLOYMENT_QUESTIONS = [
    (
        "Are GCP resources deployed using Infrastructure as Code (Deployment Manager, Terraform)?",
        7.0,
        "deployment_automation",
        "Infrastructure as Code tools like Google Cloud Deployment Manager and Terraform enable declarative, version-controlled definition of GCP resources. This approach ensures reproducible deployments, simplifies environment management, and provides auditable infrastructure changes.",
        "https://cloud.google.com/deployment-manager/docs"
    ),
    (
        "Are Secret Manager and Workload Identity used for secure credential management?",
        8.0,
        "deployment_security",
        "Google Cloud Secret Manager stores API keys, passwords, and certificates securely with automatic encryption and access controls. Workload Identity eliminates service account key files by allowing workloads to authenticate using Kubernetes service accounts, reducing credential exposure.",
        "https://cloud.google.com/secret-manager/docs/overview"
    ),
    (
        "Are Cloud Monitoring (formerly Stackdriver) and Cloud Logging configured for observability?",
        7.0,
        "deployment_monitoring",
        "Google Cloud Monitoring and Cloud Logging provide comprehensive visibility into your applications and infrastructure through metrics, logs, and traces. These services enable real-time monitoring, troubleshooting, and alerting for optimal system performance and reliability.",
        "https://cloud.google.com/monitoring/docs"
    ),
    (
        "Are IAM policies and Organization Policies enforced with least privilege access?",
        7.0,
        "deployment_security",
        "Google Cloud IAM enables fine-grained access control through roles and permissions, while Organization Policies enforce centralized constraints across your resources. Implementing least privilege ensures users and services have only the access they need to perform their functions.",
        "https://cloud.google.com/iam/docs/overview"
    ),
    (
        "Are disaster recovery strategies and automated backups configured for critical data?",
        6.0,
        "deployment_reliability",
        "GCP provides various backup and disaster recovery solutions including automated snapshots, backup schedules, and cross-region replication. Implementing these strategies protects your critical data and ensures business continuity in case of failures or disasters.",
        "https://cloud.google.com/architecture/dr-scenarios-planning-guide"
    ),
]

# On-Premise Deployment Questions
ON_PREMISE_DEPLOYMENT_QUESTIONS = [
    (
        "Are infrastructure configurations managed as code (Ansible, Puppet, Chef, Terraform)?",
        7.0,
        "deployment_automation",
        "Configuration management tools like Ansible, Puppet, Chef, and Terraform enable automated, consistent infrastructure provisioning and management. These tools treat infrastructure as code, providing version control, repeatability, and reduced manual configuration errors.",
        "https://www.ansible.com/overview/how-ansible-works"
    ),
    (
        "Are secrets and credentials stored in secure vaults (HashiCorp Vault, CyberArk)?",
        8.0,
        "deployment_security",
        "Enterprise vault solutions like HashiCorp Vault and CyberArk provide centralized, secure storage for secrets with encryption, access controls, and audit trails. Dynamic secret generation and automatic rotation capabilities further enhance security by limiting credential lifetime and exposure.",
        "https://www.vaultproject.io/docs/what-is-vault"
    ),
    (
        "Are centralized logging and monitoring systems (ELK, Prometheus, Grafana) configured?",
        7.0,
        "deployment_monitoring",
        "Centralized logging with ELK stack (Elasticsearch, Logstash, Kibana) and monitoring with Prometheus and Grafana provide comprehensive observability for on-premise infrastructure. These tools aggregate logs and metrics, enabling efficient troubleshooting, alerting, and performance analysis.",
        "https://www.elastic.co/elastic-stack"
    ),
    (
        "Are access controls and network segmentation enforced for production environments?",
        7.0,
        "deployment_security",
        "Network segmentation divides your infrastructure into isolated zones with controlled access between them, limiting lateral movement during security incidents. Combined with strict access controls, this defense-in-depth approach protects production environments from unauthorized access and breaches.",
        "https://www.cisecurity.org/insights/white-papers/cis-controls-v8"
    ),
    (
        "Are regular backups and disaster recovery procedures tested and documented?",
        6.0,
        "deployment_reliability",
        "Implementing regular backup schedules and maintaining documented disaster recovery procedures ensures your organization can recover from data loss or system failures. Regular testing of recovery procedures validates their effectiveness and identifies gaps before actual disasters occur.",
        "https://www.ready.gov/business/implementation/IT"
    ),
]

# Kubernetes Deployment Questions
KUBERNETES_DEPLOYMENT_QUESTIONS = [
    (
        "Are Kubernetes manifests managed using GitOps practices (ArgoCD, FluxCD)?",
        7.0,
        "deployment_automation",
        "GitOps tools like ArgoCD and FluxCD automate Kubernetes deployments by continuously synchronizing cluster state with Git repositories. This declarative approach provides version control for cluster configurations, automated rollbacks, and a complete audit trail of infrastructure changes.",
        "https://argo-cd.readthedocs.io/en/stable/"
    ),
    (
        "Are secrets managed using external secret managers (Sealed Secrets, External Secrets Operator)?",
        8.0,
        "deployment_security",
        "External secret management solutions keep sensitive data out of Kubernetes manifests and Git repositories by integrating with secure vaults. Tools like Sealed Secrets and External Secrets Operator enable encrypted secret storage in Git while synchronizing actual secrets from external sources at runtime.",
        "https://external-secrets.io/latest/"
    ),
    (
        "Are monitoring and logging solutions (Prometheus, Grafana, Loki) deployed in the cluster?",
        7.0,
        "deployment_monitoring",
        "Deploying Prometheus for metrics, Grafana for visualization, and Loki for logs provides comprehensive observability within Kubernetes clusters. This monitoring stack enables real-time performance tracking, alerting on issues, and detailed troubleshooting of containerized applications.",
        "https://prometheus.io/docs/introduction/overview/"
    ),
    (
        "Are RBAC policies and Network Policies enforced to restrict access and traffic?",
        7.0,
        "deployment_security",
        "Kubernetes RBAC controls who can access cluster resources and what actions they can perform, while Network Policies restrict pod-to-pod communication. Together, these features implement defense-in-depth by controlling both access and network traffic within your cluster.",
        "https://kubernetes.io/docs/reference/access-authn-authz/rbac/"
    ),
    (
        "Are Persistent Volume backups and cluster disaster recovery plans in place?",
        6.0,
        "deployment_reliability",
        "Implementing backup solutions for Persistent Volumes and maintaining cluster disaster recovery plans protects your stateful applications and data. Tools like Velero enable automated backups of cluster resources and volumes, ensuring you can recover from failures or migrate workloads between clusters.",
        "https://velero.io/docs/"
    ),
]


# Pillar metadata (updated with CI/CD and Deployment pillars)
PILLAR_METADATA = {
    # Repository pillars
    "security": {
        "name": "Security & Compliance",
        "description": "Security scanning, secrets management, and compliance checks"
    },
    "governance": {
        "name": "Governance & Access Control",
        "description": "Organizations, teams, permissions, and access policies"
    },
    "code_review": {
        "name": "Code Review & Quality",
        "description": "Pull requests, branch protection, and review processes"
    },
    "repository_management": {
        "name": "Repository Management",
        "description": "Repository structure, naming, cleanup, and organization"
    },
    "process_metrics": {
        "name": "Process & Metrics",
        "description": "KPIs, monitoring, and continuous improvement"
    },
    # CI/CD pillars
    "cicd_security": {
        "name": "CI/CD Security",
        "description": "Pipeline security, secrets management, and access controls"
    },
    "cicd_governance": {
        "name": "CI/CD Governance",
        "description": "Pipeline management, approvals, and audit trails"
    },
    "cicd_quality": {
        "name": "CI/CD Quality",
        "description": "Testing, validation, and deployment practices"
    },
    # Deployment pillars
    "deployment_automation": {
        "name": "Deployment Automation",
        "description": "Infrastructure as Code and automated deployments"
    },
    "deployment_security": {
        "name": "Deployment Security",
        "description": "Access controls, secrets management, and compliance"
    },
    "deployment_monitoring": {
        "name": "Deployment Monitoring",
        "description": "Logging, metrics, and alerting infrastructure"
    },
    "deployment_reliability": {
        "name": "Deployment Reliability",
        "description": "Backup, disaster recovery, and high availability"
    }
}


def get_questions_for_platforms(
    repo_tool: RepositoryTool,
    cicd_platform: CICDPlatform,
    deployment_platform: DeploymentPlatform
) -> Dict[str, Pillar]:
    """
    Get 15 questions (5 per category) based on selected platforms
    Total score will always equal 100 points
    
    Args:
        repo_tool: Selected repository platform
        cicd_platform: Selected CI/CD platform
        deployment_platform: Selected deployment platform
        
    Returns:
        Dictionary of pillar_id -> Pillar with questions, totaling exactly 100 points
    """
    # Map platforms to their question sets (5 questions each)
    repo_questions_map = {
        RepositoryTool.GITHUB: GITHUB_QUESTIONS,
        RepositoryTool.GITLAB: GITLAB_QUESTIONS,
        RepositoryTool.AZURE_DEVOPS: AZURE_DEVOPS_QUESTIONS,
        RepositoryTool.BITBUCKET: BITBUCKET_QUESTIONS,
    }
    
    cicd_questions_map = {
        CICDPlatform.GITHUB_ACTIONS: GITHUB_ACTIONS_QUESTIONS,
        CICDPlatform.AZURE_PIPELINES: AZURE_PIPELINES_QUESTIONS,
        CICDPlatform.GITLAB_CI: GITLAB_CI_QUESTIONS,
        CICDPlatform.JENKINS: JENKINS_QUESTIONS,
        CICDPlatform.CIRCLECI: CIRCLECI_QUESTIONS,
    }
    
    deployment_questions_map = {
        DeploymentPlatform.AZURE: AZURE_DEPLOYMENT_QUESTIONS,
        DeploymentPlatform.AWS: AWS_DEPLOYMENT_QUESTIONS,
        DeploymentPlatform.GCP: GCP_DEPLOYMENT_QUESTIONS,
        DeploymentPlatform.ON_PREMISE: ON_PREMISE_DEPLOYMENT_QUESTIONS,
        DeploymentPlatform.KUBERNETES: KUBERNETES_DEPLOYMENT_QUESTIONS,
    }
    
    # Get selected questions (15 total: 5 repo + 5 CI/CD + 5 deployment)
    selected_repo = repo_questions_map[repo_tool]
    selected_cicd = cicd_questions_map[cicd_platform]
    selected_deployment = deployment_questions_map[deployment_platform]
    
    # Combine all questions with category prefix
    all_questions = []
    question_counter = 1
    
    # Repository questions (5)
    for question_text, importance, pillar_category, description, doc_url in selected_repo:
        all_questions.append((
            f"repo_{question_counter}",
            question_text,
            importance,
            pillar_category,
            "repository",
            description,
            doc_url
        ))
        question_counter += 1
    
    # CI/CD questions (5)
    question_counter = 1
    for question_text, importance, pillar_category, description, doc_url in selected_cicd:
        all_questions.append((
            f"cicd_{question_counter}",
            question_text,
            importance,
            pillar_category,
            "cicd",
            description,
            doc_url
        ))
        question_counter += 1
    
    # Deployment questions (5)
    question_counter = 1
    for question_text, importance, pillar_category, description, doc_url in selected_deployment:
        all_questions.append((
            f"deploy_{question_counter}",
            question_text,
            importance,
            pillar_category,
            "deployment",
            description,
            doc_url
        ))
        question_counter += 1
    
    # Group questions by pillar
    pillar_groups = {}
    for question_id, question_text, importance, pillar_category, category_type, description, doc_url in all_questions:
        if pillar_category not in pillar_groups:
            pillar_groups[pillar_category] = []
        pillar_groups[pillar_category].append((
            question_id, question_text, importance, pillar_category, description, doc_url
        ))
    
    # Calculate total importance across all questions
    total_importance = sum(importance for _, _, importance, _, _, _, _ in all_questions)
    
    # Each category gets 33.33% of 100 points (repo, CI/CD, deployment)
    # Within each category, distribute based on question importance
    
    # Calculate importance per category
    repo_importance = sum(imp for _, _, imp, _, cat, _, _ in all_questions if cat == "repository")
    cicd_importance = sum(imp for _, _, imp, _, cat, _, _ in all_questions if cat == "cicd")
    deploy_importance = sum(imp for _, _, imp, _, cat, _, _ in all_questions if cat == "deployment")
    
    # Distribute 100 points proportionally across categories based on total importance
    category_weights = {
        "repository": (repo_importance / total_importance) * 100,
        "cicd": (cicd_importance / total_importance) * 100,
        "deployment": (deploy_importance / total_importance) * 100,
    }
    
    # Build pillars with proper score distribution
    pillars = {}
    for pillar_id, questions_data in pillar_groups.items():
        pillar_metadata = PILLAR_METADATA[pillar_id]
        
        # Calculate this pillar's total importance
        pillar_total_importance = sum(imp for _, _, imp, _, _, _ in questions_data)
        
        # Determine which category this pillar belongs to
        first_question_id = questions_data[0][0]
        if first_question_id.startswith("repo_"):
            category_weight = category_weights["repository"]
            category_importance = repo_importance
        elif first_question_id.startswith("cicd_"):
            category_weight = category_weights["cicd"]
            category_importance = cicd_importance
        else:  # deploy_
            category_weight = category_weights["deployment"]
            category_importance = deploy_importance
        
        # This pillar gets a portion of the category weight proportional to its importance
        pillar_weight = (pillar_total_importance / category_importance) * category_weight
        
        # Distribute pillar weight across questions based on their importance
        pillar_questions = []
        for question_id, question_text, importance, _, description, doc_url in questions_data:
            question_score = (importance / pillar_total_importance) * pillar_weight
            pillar_questions.append(
                Question(
                    id=question_id,
                    text=question_text,
                    max_score=round(question_score, 2),
                    importance=importance,
                    pillar=pillar_id,
                    description=description,
                    doc_url=doc_url
                )
            )
        
        pillars[pillar_id] = Pillar(
            name=pillar_metadata["name"],
            total_weight=round(sum(q.max_score for q in pillar_questions), 2),
            questions=pillar_questions
        )
    
    # Ensure total is exactly 100 points
    total = sum(pillar.total_weight for pillar in pillars.values())
    if abs(total - 100.0) > 0.01:
        # Adjust the largest question in the largest pillar
        largest_pillar = max(pillars.values(), key=lambda p: p.total_weight)
        largest_question = max(largest_pillar.questions, key=lambda q: q.max_score)
        adjustment = 100.0 - total
        largest_question.max_score = round(largest_question.max_score + adjustment, 2)
        largest_pillar.total_weight = round(largest_pillar.total_weight + adjustment, 2)
    
    return pillars


def get_questions_for_tool(tool: RepositoryTool) -> Dict[str, Pillar]:
    """
    Get predefined questions for a specific repository tool, organized by pillars
    
    Args:
        tool: The repository tool (GitHub, GitLab, or Azure DevOps)
        
    Returns:
        Dictionary of pillar_id -> Pillar with questions
    """
    # Tool-specific questions
    tool_questions_map = {
        RepositoryTool.GITHUB: GITHUB_QUESTIONS,
        RepositoryTool.GITLAB: GITLAB_QUESTIONS,
        RepositoryTool.AZURE_DEVOPS: AZURE_DEVOPS_QUESTIONS,
        RepositoryTool.BITBUCKET: BITBUCKET_QUESTIONS,
    }
    
    tool_questions = tool_questions_map[tool]
    
    # Group questions by pillar
    pillar_groups = {}
    for i, (question_text, importance, pillar_category, description, doc_url) in enumerate(tool_questions):
        if pillar_category not in pillar_groups:
            pillar_groups[pillar_category] = []
        pillar_groups[pillar_category].append((i, question_text, importance, pillar_category, description, doc_url))
    
    # Step 1: Calculate pillar weights based on total importance per pillar
    pillar_importance_totals = {}
    for pillar_id, questions in pillar_groups.items():
        pillar_importance_totals[pillar_id] = sum(importance for _, _, importance, _, _, _ in questions)
    
    total_all_importance = sum(pillar_importance_totals.values())
    
    # Distribute 100 points across pillars proportionally to their total importance
    pillar_target_weights = {}
    for pillar_id, pillar_importance in pillar_importance_totals.items():
        pillar_target_weights[pillar_id] = (pillar_importance / total_all_importance) * 100.0
    
    # Step 2: Within each pillar, distribute pillar weight across questions based on their importance
    pillars = {}
    for pillar_id, questions in pillar_groups.items():
        pillar_metadata = PILLAR_METADATA[pillar_id]
        pillar_target_weight = pillar_target_weights[pillar_id]
        pillar_total_importance = pillar_importance_totals[pillar_id]
        
        pillar_questions = [
            Question(
                id=f"{tool.value}_{i+1}",
                text=question_text,
                max_score=round((importance / pillar_total_importance) * pillar_target_weight, 2),
                importance=importance,
                pillar=pillar_id,
                description=description,
                doc_url=doc_url
            )
            for i, question_text, importance, _, description, doc_url in questions
        ]
        
        # Calculate actual total weight for this pillar
        pillar_weight = sum(q.max_score for q in pillar_questions)
        
        pillars[pillar_id] = Pillar(
            name=pillar_metadata["name"],
            total_weight=round(pillar_weight, 2),
            questions=pillar_questions
        )
    
    # Step 3: Ensure total is exactly 100 points by adjusting the largest pillar's largest question
    total = sum(pillar.total_weight for pillar in pillars.values())
    if abs(total - 100.0) > 0.01:
        # Find the pillar with the highest weight and adjust its highest-scoring question
        largest_pillar = max(pillars.values(), key=lambda p: p.total_weight)
        largest_question = max(largest_pillar.questions, key=lambda q: q.max_score)
        adjustment = 100.0 - total
        largest_question.max_score = round(largest_question.max_score + adjustment, 2)
        largest_pillar.total_weight = round(largest_pillar.total_weight + adjustment, 2)
    
    return pillars


def get_all_questions(pillars: Dict[str, Pillar]) -> List[tuple[str, Question, str]]:
    """Get all questions with their pillar context"""
    questions = []
    for pillar_id, pillar in pillars.items():
        for question in pillar.questions:
            questions.append((pillar_id, question, pillar.name))
    return questions

