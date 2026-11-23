# MAANRO BRAND GUIDELINES — TYPOGRAPHY ADDENDUM

FONT FAMILY: SORA & MANROPE

This addendum specifies the official typefaces for Maanro brand identity, to be used alongside the existing brand colour palette (Obsidian Black #080808 + Growth Green #32CD32, 60/30/10 allocation) and logo usage rules.

1. PRIMARY FONT: SORA
   - Google Fonts: https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600
   - Classification: Modern, confident and geometric sans-serif
   - Brand rationale: Gives Maanro a premium technology feel, distinguishes from generic AI startups
   - Available weights:
     • 400 (Regular) — Body text, secondary information
     • 500 (Medium) — Subheadings, secondary headlines
     • 600 (SemiBold) — Main headings, titles, key statements

   • USE cases:
     – Headlines and page titles
     – Section titles and section dividers
     – Key statements and value propositions
     – Feature section headers
     – Pricing tier headers (Tier 1, Tier 2, Tier 3)
     – Plan comparison section headers

   • DO NOT:
     – Use for body paragraphs or extended text
     – Use smaller than 16px in digital formats
     – Combine with competing decorative fonts

2. SECONDARY FONT: MANROPE
   - Google Fonts: https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600
   - Classification: Clean, refined and highly readable sans-serif
   - Brand rationale: Balances Sora without competing; ensures readability across all media
   - Available weights:
     • 400 (Regular) — Body text, general text
     • 500 (Medium) — Subtle emphasis, inline headings
     • 600 (SemiBold) — Buttons, labels, captions

   • USE cases:
     – Body paragraphs and articles
     – Navigation menu items
     – Form labels and input placeholders
     – Button text and microcopy
     – Captions and supporting text
     – Pricing details and feature descriptions
     – Privacy policy and legal text

   • DO NOT:
     – Use for main headlines or page titles
     – Use for display text larger than 24px in most contexts
     – Mix weights inconsistently (e.g., do not use 600 for body text)

3. TYPOGRAPHY RULES & RECOMMENDATIONS

   • Font Size Hierarchy (Digital):
     – H1 / Main headline: Sora 600, 3.5rem (desktop), 2.5rem (mobile)
     – H2 / Subheading: Sora 500, 2.5rem
     – Body copy: Manrope 400, 1rem (16px minimum)
     – Button / Label text: Manrope 600, 1rem
     – Caption / Small text: Manrope 400, 0.875rem

   • Letter Spacing:
     – Sora headings: Slightly wider tracking for uppercase (0.03em–0.05em)
     – Manrope uppercase labels: 0.05em wider tracking
     – Do not compress or extend fonts beyond normal proportions

   • Line Height:
     – Manrope body text: 1.6 line height
     – Sora headings: 1.2–1.3 line height

   • Color Usage:
     – Primary text: Obsidian Black #080808 on white/light backgrounds
     – Secondary text: Growth Green #32CD32 on white/light backgrounds
     – White text: On dark backgrounds (Obsidian Black #080808 sections)
     – Contrast ratio: Minimum 4.5:1 for normal text, 3:1 for large text

   • MAANRO Logo Lettering:
     – Keep existing logo lettering unchanged
     – Do not reletter or modify the MAANRO wordmark
     – Use the established Oxblood Burgundy #240710 (MAAN) and Champagne Bronze #B78A55 (RO) or the new Obsidian Black #080808 + Growth Green #32CD32 versions
     – Surrounding typography should support, not compete with, the logo

4. MEDIA APPLICATION

   • Web / Digital:
     – Web fonts loaded via Google Fonts @import
     – System fallback: Sora → Helvetica/Arial, Manrope → Helvetica/Arial
     – Responsive typography scales with viewport
     – Print stylesheet specifies 100% font size, 1.2 line height

   • Print / Physical:
     – Print-quality font rendering at 300 DPI minimum
     – May use local font equivalents if web fonts not permitted
     – Color printing: Obsidian Black ink for black, Pantone 32CD32 for green

   • Motion / Video:
     – Animated text uses Sora for titles, Manrope for body
     – Lower thirds and captions use Manrope Regular 400
     – Title cards use Sora SemiBold 600
     – animation duration respects readability (min 0.3s)

5. EXAMPLE USAGE

   /* CSS VARIABLES (recommended) */
   :root {
       --font-sora: 'Sora', sans-serif;
       --font-manrope: 'Manrope', sans-serif;
       --sora-regular: normal;
       --sora-medium: 500;
       --sora-semiBold: 600;
       --manrope-regular: normal;
       --manrope-medium: 500;
       --manrope-semiBold: 600;
   }

   /* Heading font: Sora */
   h1, h2, h3, h4, h5, h6 {
       font-family: 'Sora', sans-serif;
   }
   h1 { font-weight: 600; } /* Sora SemiBold */
   h2 { font-weight: 500; } /* Sora Medium */

   /* Body font: Manrope */
   p, .body-text {
       font-family: 'Manrope', sans-serif;
       font-weight: 400;
       line-height: 1.6;
   }

   /* Button and label font: Manrope SemiBold */
   .button, .label {
       font-family: 'Manrope', sans-serif;
       font-weight: 600;
       letter-spacing: 0.05em;
   }

6. IMPLEMENTATION CHECKLIST

   ☐ Add @import Google Fonts to all web pages
   ☐ Update CSS variables or global font stacks
   ☐ Replace all body text from previous font to Manrope 400
   • Replace all headings from previous font to Sora (600/500)
   • Update button text to Manrope 600 with 0.05em letter-spacing
   • Update pricing tier headers to Sora SemiBold 600
   • Update plan comparison headers to Sora Medium 500
   • Preserve existing MAANRO logo lettering unchanged
   • Test readability at all screen sizes (320px–1440px+)
   • Verify contrast ratios with Obsidian Black #080808 and Growth Green #32CD32
   • Update any print collateral with font specifications
   • Notify design team and external vendors of new font requirements
   • Update any third-party templates or materials

7. CONTACT & SUPPORT

   For questions about font implementation, rendering issues, or accessibility reviews,
   contact the brand team or refer to the full Maanro Brand Guidelines document.

   — End of Typographic Addendum —