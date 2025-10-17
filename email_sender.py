# email_sender.py
"""
邮件发送模块
支持 SMTP 发送 HTML 格式的研究简报
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from dotenv import load_dotenv
import logging
import markdown

logger = logging.getLogger(__name__)

load_dotenv()


def markdown_to_html(md_text):
    """
    将 Markdown 文本转换为 HTML
    
    Args:
        md_text: Markdown 格式的文本
        
    Returns:
        str: HTML 格式的文本
    """
    # 使用 markdown 库转换
    html = markdown.markdown(
        md_text,
        extensions=['extra', 'codehilite', 'tables', 'fenced_code']
    )
    
    # 添加 CSS 样式
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-left: 4px solid #3498db;
                padding-left: 15px;
            }}
            h3 {{
                color: #7f8c8d;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            code {{
                background-color: #f8f9fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }}
            pre {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            blockquote {{
                border-left: 4px solid #e74c3c;
                padding-left: 15px;
                margin-left: 0;
                color: #7f8c8d;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                text-align: center;
                color: #7f8c8d;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {html}
            <div class="footer">
                <p>📧 这是一封自动生成的 BioRxiv 肿瘤学研究简报邮件</p>
                <p>如有问题，请联系系统管理员</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return styled_html


def send_email(subject, body_markdown, recipient=None):
    """
    发送邮件
    
    Args:
        subject: 邮件主题
        body_markdown: Markdown 格式的邮件正文
        recipient: 收件人邮箱（可选，默认从环境变量读取）
        
    Returns:
        bool: 发送成功返回 True，失败返回 False
    """
    try:
        # 从环境变量获取邮件配置
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        sender_email = os.getenv("SMTP_SENDER_EMAIL")
        smtp_password = os.getenv("SMTP_PASSWORD")
        recipient_email = recipient or os.getenv("EMAIL_RECIPIENT")
        
        # 验证必要的配置
        if not all([smtp_server, sender_email, smtp_password, recipient_email]):
            logger.error("邮件配置不完整，请检查环境变量")
            return False
        
        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        # QQ邮箱要求 From 必须是实际的发件人邮箱地址
        msg['From'] = f'BioRxiv <{sender_email}>'
        msg['To'] = recipient_email
        msg['Subject'] = Header(subject, 'utf-8')
        
        # 添加纯文本版本（作为备用）
        text_part = MIMEText(body_markdown, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # 添加 HTML 版本
        html_body = markdown_to_html(body_markdown)
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 连接 SMTP 服务器并发送
        logger.info(f"正在连接 SMTP 服务器: {smtp_server}:{smtp_port}")
        
        server = None
        try:
            if smtp_port == 465:
                # SSL 连接
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
            else:
                # STARTTLS 连接
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                server.ehlo()  # 识别身份
                server.starttls()  # 启动 TLS
                server.ehlo()  # 再次识别身份
            
            logger.info("正在登录...")
            server.login(sender_email, smtp_password)
            
            logger.info(f"正在发送邮件到: {recipient_email}")
            server.sendmail(sender_email, [recipient_email], msg.as_string())
            
            logger.info(f"✅ 邮件发送成功到: {recipient_email}")
            return True
            
        finally:
            # 确保连接关闭
            if server:
                try:
                    server.quit()
                except:
                    pass
        
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP 错误: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 邮件发送失败: {e}")
        return False


def send_digest_email(period_label, summary_text):
    """
    发送研究简报邮件
    
    Args:
        period_label: 期别标签（早报/晚报）
        summary_text: 摘要文本（Markdown 格式）
        
    Returns:
        bool: 发送成功返回 True
    """
    from datetime import datetime
    
    # 生成邮件主题
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    subject = f"📬 BioRxiv 肿瘤学研究{period_label} - {current_time}"
    
    # 发送邮件
    return send_email(subject, summary_text)


def send_error_notification(error_msg):
    """
    发送错误通知邮件
    
    Args:
        error_msg: 错误信息
        
    Returns:
        bool: 发送成功返回 True
    """
    from datetime import datetime
    
    subject = f"⚠️ BioRxiv 系统错误通知 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    body = f"""
# 系统错误通知

发生时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 错误信息

```
{error_msg}
```

请及时检查系统日志并处理。

---

这是一封自动生成的错误通知邮件。
"""
    
    return send_email(subject, body)

