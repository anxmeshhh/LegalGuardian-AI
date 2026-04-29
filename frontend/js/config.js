/**
 * LegalGuardian AI — Configuration
 * API endpoints, sample contracts, and constants
 */

const CONFIG = {
    API_BASE: window.location.origin,
    ENDPOINTS: {
        ANALYZE: '/api/analyze',
        ANALYZE_FILE: '/api/analyze-file',
        QA: '/api/qa',
        DOC_TYPES: '/api/doc-types',
        HEALTH: '/api/health'
    }
};

// Sample contracts for quick testing
const SAMPLE_CONTRACTS = {
    employment: `EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into as of January 15, 2025 ("Effective Date"), by and between TechVentures Inc., a Delaware corporation ("Employer"), and John Smith ("Employee").

Section 1. Position and Duties
The Employer hereby employs the Employee as a Senior Software Engineer. The Employee shall perform all duties as assigned by the Employer and shall devote full-time effort to the Employer's business.

Section 2. Compensation
The Employee shall receive an annual base salary of $120,000, payable in bi-weekly installments. The Employer may, at its sole discretion, award performance bonuses.

Section 3. Term and Termination
This Agreement shall commence on the Effective Date and continue for a period of two (2) years, automatically renewing for successive one-year terms unless either party provides sixty (60) days' written notice of non-renewal. The Employer may terminate this Agreement at any time, for any reason or no reason, with thirty (30) days' written notice. The Employee may terminate with sixty (60) days' written notice.

Section 4. Confidentiality
The Employee agrees to maintain strict confidentiality regarding all proprietary information, trade secrets, client lists, business strategies, and technical data of the Employer, both during and after the term of employment, in perpetuity.

Section 5. Intellectual Property Assignment
All inventions, discoveries, designs, code, documentation, and other works of authorship created by the Employee during the term of employment, whether or not created during working hours or using the Employer's resources, shall be the sole and exclusive property of the Employer. The Employee hereby irrevocably assigns all right, title, and interest in such works to the Employer.

Section 6. Non-Compete Covenant
For a period of two (2) years following the termination of this Agreement, the Employee shall not, directly or indirectly, engage in any business that competes with the Employer's business within a 100-mile radius of any Employer office location.

Section 7. Indemnification
The Employee shall indemnify, defend, and hold harmless the Employer from and against any and all claims, damages, losses, liabilities, costs, and expenses arising out of or related to the Employee's performance of duties or breach of this Agreement.

Section 8. Limitation of Liability
The Employer's total liability to the Employee shall not exceed the Employee's base salary for the preceding three (3) months. In no event shall the Employer be liable for any indirect, incidental, consequential, or punitive damages.

Section 9. Governing Law
This Agreement shall be governed by the laws of the State of Delaware.`,

    rental: `RESIDENTIAL LEASE AGREEMENT

This Residential Lease Agreement ("Lease") is entered into as of March 1, 2025, by and between Greenfield Properties LLC ("Landlord") and Alex Rivera ("Tenant").

Section 1. Premises
The Landlord agrees to lease to the Tenant the residential property located at 456 Oak Street, Apt 3B, Austin, TX 78701 for use as a private residence only.

Section 2. Term
The initial lease term shall be twelve (12) months. This Lease shall automatically renew for successive twelve-month terms unless the Tenant provides written notice of non-renewal at least ninety (90) days prior to expiration. The Landlord may elect not to renew by providing thirty (30) days' notice.

Section 3. Rent
The Tenant shall pay monthly rent of $2,200, due on the first day of each month. A late fee of $150 shall be charged for any payment received after the fifth day. The Landlord reserves the right to increase rent by up to 15% upon each renewal, at the Landlord's sole discretion.

Section 4. Security Deposit
The Tenant shall pay a security deposit of $4,400. The Landlord may deduct from the security deposit any amounts for damages, unpaid rent, cleaning fees, and any other costs as determined by the Landlord in its sole discretion.

Section 5. Maintenance and Repairs
The Tenant shall be responsible for all maintenance and repairs to the Premises, including plumbing, electrical, HVAC systems, appliances, and structural elements.

Section 6. Liability and Indemnification
The Tenant shall indemnify and hold harmless the Landlord from any and all claims arising from the Tenant's use of the Premises. The Landlord shall have no liability for any damage to the Tenant's property, regardless of cause, including the Landlord's own negligence.

Section 7. Early Termination
If the Tenant terminates this Lease early, the Tenant shall pay a termination fee equal to three (3) months' rent plus forfeit the entire security deposit. The Landlord may terminate at any time with fourteen (14) days' notice.

Section 8. Governing Law
This Lease shall be governed by the laws of the State of Texas.`,

    freelance: `FREELANCE SERVICE AGREEMENT

This Agreement is entered into as of February 10, 2025, by and between Digital Solutions Corp. ("Client") and Priya Sharma ("Service Provider").

Section 1. Scope of Work
The Service Provider shall design and develop a custom e-commerce website, including front-end design, back-end development, payment integration, and CMS setup.

Section 2. Compensation
The Client shall pay a total fee of $15,000: 10% upon signing, 40% upon design completion, and 50% upon final delivery. Payment within forty-five (45) days of each invoice. Late payments shall not accrue interest.

Section 3. Timeline
The Service Provider shall complete all deliverables within ninety (90) days. Failure to meet this deadline entitles the Client to a 5% discount per week of delay, up to 25%.

Section 4. Intellectual Property
All work product created by the Service Provider shall be the sole and exclusive property of the Client. The Service Provider irrevocably assigns all intellectual property rights to the Client. The Service Provider shall not retain copies or display the work in any portfolio without prior written consent.

Section 5. Non-Compete
For twelve (12) months following completion or termination, the Service Provider shall not provide similar services to any direct competitor of the Client, as determined by the Client in its sole discretion.

Section 6. Indemnification
The Service Provider shall indemnify the Client from any and all claims arising from the Service Provider's work, including IP infringement and defects.

Section 7. Liability
The Service Provider's liability under this Agreement shall be unlimited. The Client's liability shall not exceed the fees actually paid.

Section 8. Termination
The Client may terminate at any time with seven (7) days' notice. The Service Provider may terminate only for material breach after thirty (30) days' notice.

Section 9. Governing Law
This Agreement shall be governed by the laws of the State of California.`
};
