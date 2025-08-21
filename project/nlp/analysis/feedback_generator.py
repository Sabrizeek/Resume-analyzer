import re

def generate_resume_tips(text, basic_info):
    tips = []

    # 1. Check for Action Verbs
    action_verbs = ['developed', 'managed', 'led', 'created', 'implemented', 'designed', 'analyzed', 'optimized', 'automated']
    lines = text.split('\n')
    action_verb_count = 0
    for line in lines:
        if any(line.strip().lower().startswith(verb) for verb in action_verbs):
            action_verb_count += 1
            
    if action_verb_count < 5:
        tips.append("💡 **Action Verbs**: Strengthen your experience bullet points by starting them with powerful action verbs like 'Developed', 'Managed', or 'Optimized'.")
    else:
        tips.append("✅ **Action Verbs**: Great use of action verbs to describe your accomplishments!")

    # 2. Check for Quantifiable Metrics
    if not re.search(r'\d+%', text) and not re.search(r'[\$€£]\d+', text) and not re.search(r'\steam of \d', text):
         tips.append("💡 **Quantifiable Metrics**: Your resume could be more impactful. Try to include numbers and metrics to quantify your achievements (e.g., 'Increased efficiency by 15%' or 'Managed a budget of $50k').")
    else:
        tips.append("✅ **Quantifiable Metrics**: Excellent job including measurable results and metrics in your experience.")

    # 3. Check Resume Length (based on page count)
    if basic_info.get('pages', 0) > 2:
        tips.append("💡 **Resume Length**: Your resume is longer than 2 pages. For most roles, a concise 1-2 page resume is preferred. Review for brevity.")
    elif basic_info.get('pages', 0) == 0:
         tips.append("⚠️ **Resume Length**: Could not determine the page count. Ensure the document is a standard PDF.")
    else:
        tips.append("✅ **Resume Length**: Your resume length is concise and professional.")

    # 4. Contact Information Check
    if basic_info.get('email') == "Not Found" or basic_info.get('phone') == "Not Found":
        tips.append("⚠️ **Contact Information**: Crucial contact information (email or phone number) seems to be missing. Make sure it's clearly visible at the top of your resume.")
    else:
        tips.append("✅ **Contact Information**: Contact details are present and accounted for.")
        
    return tips