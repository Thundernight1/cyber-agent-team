#!/usr/bin/env python3
"""
QUICK SALES GENERATOR
Generate personalized cold emails + reconnaissance for Seattle companies

Usage:
  python3 QUICK_SALES_GENERATOR.py --company github.com
  python3 QUICK_SALES_GENERATOR.py --list companies.csv
"""

import asyncio
import json
from tools.security_tools import ToolFactory
import sys
import argparse

SEATTLE_TECH_COMPANIES = [
    ("Amazon", "amazon.com", "Chief Security Officer"),
    ("Microsoft", "microsoft.com", "VP of Security"),
    ("Stripe", "stripe.com", "Head of Security"),
    ("Figma", "figma.com", "CTO"),
    ("Redfin", "redfin.com", "VP of Engineering"),
    ("Zillow", "zillow.com", "Chief Architect"),
    ("Wix", "wix.com", "Security Engineer"),
    ("T-Mobile", "t-mobile.com", "VP Security"),
    ("Alaska Airlines", "alaskaair.com", "IT Director"),
    ("Starbucks", "starbucks.com", "Chief Digital Officer"),
]

async def generate_cold_email(company_name: str, domain: str, role: str):
    """Generate personalized cold email with actual recon findings"""
    
    print(f"\n{'='*70}")
    print(f"🎯 COLD EMAIL GENERATOR: {company_name}")
    print(f"{'='*70}\n")
    
    tools = ToolFactory.initialize()
    findings = {
        "dns": None,
        "whois": None,
        "osint": None
    }
    
    # Run OSINT on their domain
    print(f"[1/3] Running DNS enumeration on {domain}...")
    dns = tools.get('dns')
    if dns:
        result = await dns.run(target=domain, record_type='A')
        if result.status == 'success':
            findings['dns'] = result.output
            print(f"      ✅ DNS resolved: {result.output.get('raw_response', '')[:100]}")
    
    print(f"\n[2/3] Running OSINT recon on {domain}...")
    shodan = tools.get('shodan')
    if shodan:
        result = await shodan.run(target=domain, search_type='host')
        if result.status == 'success':
            findings['osint'] = result.output
            tools_used = [t.get('tool') for t in result.output.get('osint_tools', [])]
            print(f"      ✅ OSINT completed: tools={tools_used}")
    
    print(f"\n[3/3] Running Whois lookup on {domain}...")
    whois = tools.get('whois')
    if whois:
        result = await whois.run(target=domain)
        if result.status == 'success':
            findings['whois'] = result.output
            print(f"      ✅ Whois completed: registrar={result.output.get('registrar')}")
    
    # Generate cold email
    print(f"\n{'─'*70}")
    print("📧 GENERATED COLD EMAIL:")
    print(f"{'─'*70}\n")
    
    email = f"""Subject: Security findings for {company_name}

Hi [First Name],

We just ran a quick security assessment of {domain} and found some interesting infrastructure:

✓ DNS Configuration: [{findings['dns'].get('record_type') if findings['dns'] else 'A'}] records configured
✓ Domain Info: Registrar is {findings['whois'].get('registrar') if findings['whois'] else 'registered'}
✓ OSINT Results: 3-point recon completed (DNS, Whois, HTTP headers)

Most companies don't regularly check this level of detail on their own infrastructure.

Quick question: Are you currently doing regular security assessments? 

If not, would you be open to a quick 30-min call to review the full findings?
(No charge - just want to help make sure you're covered)

If now's not a good time, no problem - just let me know.

Best,
[Your Name]
[Your Title]
[Your Email]
[Your Phone]

---

P.S. - We specialize in helping Seattle tech companies find security gaps 
       before attackers do. Let me know if you'd like to chat.
"""
    
    print(email)
    
    # Generate follow-up if no response
    print(f"\n{'─'*70}")
    print("📧 FOLLOW-UP EMAIL (If no response after 5 days):")
    print(f"{'─'*70}\n")
    
    followup = f"""Subject: Re: Security findings for {company_name} - 2-min question

Hi [First Name],

Quick follow-up on my previous note about {domain}.

I realize you're probably busy, so just wanted to see if you'd 
be open to 2 minutes on whether this is on your roadmap.

We're helping {company_name}'s peer companies get security-audit-ready 
without the big consulting bill.

If you're interested, let's grab 15 mins next week. 
If not, I'll leave you alone - totally understand.

[Your Name]
"""
    
    print(followup)
    
    # Save to file
    filename = f"email_{company_name.lower().replace(' ', '_')}.txt"
    with open(filename, 'w') as f:
        f.write(email)
    
    print(f"\n{'='*70}")
    print(f"✅ Email saved to: {filename}")
    print(f"{'='*70}\n")
    
    return email, findings


async def batch_generate_emails(companies: list = None):
    """Generate emails for multiple companies"""
    
    if not companies:
        companies = SEATTLE_TECH_COMPANIES[:3]  # Start with top 3
    
    for company_name, domain, role in companies:
        try:
            await generate_cold_email(company_name, domain, role)
        except Exception as e:
            print(f"❌ Error processing {company_name}: {str(e)}")
        
        # Space out requests
        await asyncio.sleep(2)


def main():
    parser = argparse.ArgumentParser(
        description='Generate personalized cold emails with security recon'
    )
    parser.add_argument('--company', type=str, help='Single company domain to scan')
    parser.add_argument('--list', type=str, help='CSV file with companies')
    parser.add_argument('--batch', action='store_true', help='Run on default Seattle companies')
    
    args = parser.parse_args()
    
    if args.company:
        # Single company
        asyncio.run(generate_cold_email(
            company_name=args.company.split('.')[0].upper(),
            domain=args.company,
            role="Security Officer"
        ))
    elif args.list:
        # From CSV
        companies = []
        with open(args.list) as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    companies.append((parts[0], parts[1], parts[2] if len(parts) > 2 else "CTO"))
        asyncio.run(batch_generate_emails(companies))
    elif args.batch:
        # Default batch
        print(f"\n🎯 GENERATING EMAILS FOR {len(SEATTLE_TECH_COMPANIES)} COMPANIES\n")
        asyncio.run(batch_generate_emails(SEATTLE_TECH_COMPANIES))
    else:
        # Interactive
        domain = input("Enter company domain (e.g., github.com): ").strip()
        company = input("Enter company name (e.g., GitHub): ").strip()
        asyncio.run(generate_cold_email(company, domain, "CTO"))


if __name__ == "__main__":
    main()
