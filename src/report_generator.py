from fpdf import FPDF
import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'News Scraper Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def clean_text(text):
    if not text:
        return ""
    # Replace common smart quotes and dashes
    replacements = {
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u2013': '-', '\u2014': '-'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Encode to latin-1 with replacement for anything else
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf_report(articles, topic="General"):
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title and Metadata
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, clean_text(f'Topic: {topic}'), 0, 1, 'L')
    pdf.cell(0, 10, f'Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'L')
    pdf.cell(0, 10, f'Total Articles: {len(articles)}', 0, 1, 'L')
    pdf.ln(10)
    
    # Articles
    for article in articles:
        # Title
        pdf.set_font('Arial', 'B', 12)
        pdf.multi_cell(0, 10, clean_text(article.title))
        
        # Metadata
        pdf.set_font('Arial', 'I', 9)
        source_name = clean_text(article.source.name if article.source else "Unknown")
        date_str = article.published_date.strftime('%Y-%m-%d')
        pdf.cell(0, 5, clean_text(f"Source: {source_name} | Date: {date_str} | Sentiment: {article.sentiment}"), 0, 1)
        
        # Summary
        pdf.set_font('Arial', '', 10)
        pdf.ln(2)
        summary = clean_text(article.summary) if article.summary else "No summary available."
        pdf.multi_cell(0, 5, summary)
        
        # Link
        pdf.set_font('Arial', 'U', 9)
        pdf.set_text_color(0, 0, 255)
        pdf.cell(0, 5, "Read More", 0, 1, 'L', link=article.url)
        pdf.set_text_color(0, 0, 0)
        
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

    return pdf.output(dest='S').encode('latin-1')
