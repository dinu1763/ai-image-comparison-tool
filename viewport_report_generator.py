"""
PDF Report Generator for Viewport-by-Viewport Website Comparisons
"""

import os
from datetime import datetime
from typing import Dict, Any, List
from urllib.parse import urlparse

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, 
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from PIL import Image


class ViewportReportGenerator:
    """Generate comprehensive PDF reports for viewport comparisons"""
    
    def __init__(self):
        """Initialize the report generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='Metric',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#555555'),
            spaceAfter=4,
            fontName='Helvetica'
        ))
    
    def _create_header_footer(self, canvas_obj, doc):
        """Add header and footer to each page"""
        canvas_obj.saveState()
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawString(inch, 0.5 * inch, footer_text)
        canvas_obj.drawRightString(
            doc.pagesize[0] - inch, 
            0.5 * inch, 
            f"Page {doc.page}"
        )
        
        canvas_obj.restoreState()
    
    def _get_domain_name(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc or url
        except:
            return url
    
    def _create_summary_page(self, summary: Dict[str, Any]) -> List:
        """Create summary page elements"""
        elements = []
        
        # Title
        elements.append(Paragraph(
            "Website Viewport Comparison Report",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.3 * inch))
        
        # Comparison info - display full URLs
        url1 = summary['url1']
        url2 = summary['url2']
        
        elements.append(Paragraph(
            f"<b>Website 1:</b> {url1}",
            self.styles['CustomBody']
        ))
        elements.append(Paragraph(
            f"<b>Website 2:</b> {url2}",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        # Summary statistics table
        summary_data = [
            ['Metric', 'Value'],
            ['Viewport Size', summary['viewport_size'].capitalize()],
            ['Viewport Dimensions', f"{summary['viewport_dimensions']['width']} x {summary['viewport_dimensions']['height']} px"],
            ['Total Viewports Compared', str(summary['total_viewports'])],
            ['Website 1 Height', f"{summary['page_height1']} px"],
            ['Website 2 Height', f"{summary['page_height2']} px"],
            ['Total Differences Detected', str(summary['total_differences'])],
        ]
        
        if summary.get('average_ssim') is not None:
            similarity_pct = summary['average_ssim'] * 100
            summary_data.append(['Average Similarity (SSIM)', f"{similarity_pct:.2f}%"])
        
        summary_data.extend([
            ['Comparison Type', summary['comparison_type'].capitalize()],
            ['AI Model Used', summary['model_used']],
            ['Analysis Date', datetime.fromisoformat(summary['timestamp']).strftime('%Y-%m-%d %H:%M:%S')]
        ])
        
        summary_table = Table(summary_data, colWidths=[3 * inch, 3.5 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Overall findings
        elements.append(Paragraph("Overall Findings", self.styles['SectionHeader']))
        
        if summary['total_differences'] == 0:
            finding = "The websites appear visually identical across all viewports."
        elif summary.get('average_ssim'):
            if summary['average_ssim'] > 0.95:
                finding = "The websites are highly similar with minor differences detected."
            elif summary['average_ssim'] > 0.85:
                finding = "The websites show moderate differences across viewports."
            else:
                finding = "The websites show significant visual differences."
        else:
            finding = f"A total of {summary['total_differences']} difference regions were detected across all viewports."
        
        elements.append(Paragraph(finding, self.styles['CustomBody']))
        elements.append(PageBreak())
        
        return elements
    
    def _resize_image_for_pdf(self, image_path: str, max_width: float, max_height: float) -> tuple:
        """
        Calculate image dimensions to fit within max width/height while maintaining aspect ratio
        
        Returns:
            Tuple of (width, height) in points
        """
        try:
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # Calculate scaling factor
            width_scale = max_width / img_width
            height_scale = max_height / img_height
            scale = min(width_scale, height_scale)
            
            # Calculate new dimensions
            new_width = img_width * scale
            new_height = img_height * scale
            
            return (new_width, new_height)
        except Exception as e:
            print(f"Error resizing image: {e}")
            return (max_width, max_height)
    
    def _create_viewport_comparison_page(self, viewport_data: Dict[str, Any], summary: Dict[str, Any]) -> List:
        """Create comparison page for a single viewport"""
        elements = []

        # Get viewport information
        viewport_num = viewport_data['viewport_number']
        total_viewports = viewport_data['total_viewports']

        # Viewport header
        elements.append(Paragraph(
            f"Viewport {viewport_num} of {total_viewports}",
            self.styles['CustomSubtitle']
        ))

        # Position info
        elements.append(Paragraph(
            f"Scroll Position: {viewport_data['scroll_position']}px",
            self.styles['Metric']
        ))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Metrics
        metrics_data = []
        if viewport_data.get('ssim_score') is not None:
            similarity_pct = viewport_data['ssim_score'] * 100
            metrics_data.append(f"<b>Similarity Score:</b> {similarity_pct:.2f}%")
        
        metrics_data.append(f"<b>Differences Detected:</b> {viewport_data['num_differences']}")
        
        for metric in metrics_data:
            elements.append(Paragraph(metric, self.styles['Metric']))
        
        elements.append(Spacer(1, 0.15 * inch))
        
        # Screenshots side by side
        # Create labels in format: domain_path
        def format_url_label(url):
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.replace('www.', '')
                path = parsed.path.strip('/')
                if path:
                    return f"{domain}_{path}".replace('/', '_')
                return domain
            except:
                return url
        
        label1 = format_url_label(summary['url1'])
        label2 = format_url_label(summary['url2'])
        
        # Calculate image dimensions (side by side)
        max_img_width = 3.5 * inch
        max_img_height = 6.5 * inch
        
        img1_dims = self._resize_image_for_pdf(viewport_data['screenshot1_path'], max_img_width, max_img_height)
        img2_dims = self._resize_image_for_pdf(viewport_data['screenshot2_path'], max_img_width, max_img_height)
        
        # Create table with screenshots
        screenshot_table_data = [
            [Paragraph(f"<b>{label1}</b>", self.styles['Metric']), 
             Paragraph(f"<b>{label2}</b>", self.styles['Metric'])],
            [RLImage(viewport_data['screenshot1_path'], width=img1_dims[0], height=img1_dims[1]),
             RLImage(viewport_data['screenshot2_path'], width=img2_dims[0], height=img2_dims[1])]
        ]
        
        screenshot_table = Table(screenshot_table_data, colWidths=[3.75 * inch, 3.75 * inch])
        screenshot_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, 0), 5),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ]))
        
        elements.append(screenshot_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Difference highlight image if available
        if viewport_data.get('highlight_path') and os.path.exists(viewport_data['highlight_path']):
            elements.append(Paragraph("Visual Differences Highlighted", self.styles['SectionHeader']))

            # Full width for highlight image
            max_highlight_width = 6.5 * inch
            max_highlight_height = 4.5 * inch
            highlight_dims = self._resize_image_for_pdf(
                viewport_data['highlight_path'],
                max_highlight_width,
                max_highlight_height
            )

            elements.append(RLImage(
                viewport_data['highlight_path'],
                width=highlight_dims[0],
                height=highlight_dims[1]
            ))
            elements.append(Spacer(1, 0.15 * inch))

        # AI Analysis
        if viewport_data.get('ai_analysis'):
            elements.append(Paragraph("AI Analysis", self.styles['SectionHeader']))

            # Format analysis as bullet points
            analysis_text = viewport_data['ai_analysis']

            # Split by newlines to get individual lines
            lines = analysis_text.split('\n')

            for line in lines:
                line = line.strip()
                if line:
                    # Remove existing bullet characters and clean up
                    clean_line = line.lstrip('•-*→ ').strip()

                    # Skip empty lines after cleaning
                    if not clean_line:
                        continue

                    # Add bullet point and format as paragraph
                    bullet_text = f"• {clean_line}"
                    elements.append(Paragraph(bullet_text, self.styles['CustomBody']))
                    elements.append(Spacer(1, 0.05 * inch))

        elements.append(PageBreak())

        return elements

    def generate_report(
        self,
        comparison_result: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        Generate PDF report from viewport comparison results

        Args:
            comparison_result: Result dictionary from ViewportComparisonTool
            output_path: Path to save the PDF report

        Returns:
            True if successful, False otherwise
        """
        try:
            if not comparison_result.get('success'):
                print(f"Cannot generate report: {comparison_result.get('error')}")
                return False

            summary = comparison_result['summary']
            viewport_comparisons = comparison_result['viewport_comparisons']

            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=0.75 * inch,
                leftMargin=0.75 * inch,
                topMargin=0.75 * inch,
                bottomMargin=0.75 * inch
            )

            # Build document elements
            elements = []

            # Add summary page
            elements.extend(self._create_summary_page(summary))

            # Add viewport comparison pages
            for viewport_data in viewport_comparisons:
                elements.extend(self._create_viewport_comparison_page(viewport_data, summary))

            # Build PDF
            doc.build(elements, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

            print(f"PDF report generated successfully: {output_path}")
            return True

        except Exception as e:
            print(f"Error generating PDF report: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_report_filename(self, url1: str, url2: str) -> str:
        """
        Generate a descriptive filename for the report

        Args:
            url1: First website URL
            url2: Second website URL

        Returns:
            Filename string
        """
        try:
            # Parse the first URL to get domain and path
            parsed = urlparse(url1)
            domain = parsed.netloc.replace('www.', '')  # Remove www. prefix
            path = parsed.path.strip('/')  # Remove leading/trailing slashes
            
            # Combine domain and path
            if path:
                filename_base = f"{domain}_{path}"
            else:
                filename_base = domain
            
            # Clean the filename - replace special characters with underscores
            filename_base = filename_base.replace('/', '_').replace('.', '_')
            filename_base = filename_base.replace(':', '_').replace('?', '_')
            filename_base = filename_base.replace('&', '_').replace('=', '_')
            
            # Get today's date
            date_str = datetime.now().strftime('%Y%m%d')
            
            # Truncate if too long (keep room for date)
            if len(filename_base) > 50:
                filename_base = filename_base[:50]
            
            return f"{filename_base}_{date_str}.pdf"
        except:
            # Fallback to timestamp-based name if parsing fails
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            return f"viewport_comparison_{timestamp}.pdf"

