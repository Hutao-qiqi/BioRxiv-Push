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
                font-family: 'Segoe UI', 'Microsoft YaHei', Arial, sans-serif;
                line-height: 1.7;
                color: #2c3e50;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            h1 {{
                color: #1a1a1a;
                font-size: 1.8em;
                font-weight: 900;
                border-bottom: 4px solid #e74c3c;
                padding-bottom: 15px;
                margin-top: 40px;
                margin-bottom: 20px;
                background: linear-gradient(to right, #f8f9fa, white);
                padding-left: 15px;
                border-left: 6px solid #e74c3c;
            }}
            h2 {{
                color: #2c3e50;
                font-size: 1.5em;
                font-weight: 800;
                margin-top: 35px;
                margin-bottom: 15px;
                border-left: 5px solid #3498db;
                padding-left: 15px;
                background-color: #f8f9fa;
                padding-top: 10px;
                padding-bottom: 10px;
            }}
            h3 {{
                color: #34495e;
                font-weight: 700;
                margin-top: 20px;
            }}
            strong, b {{
                font-weight: 900;
                color: #c0392b;
                background-color: #fff3cd;
                padding: 2px 4px;
                border-radius: 2px;
            }}
            a {{
                color: #3498db;
                text-decoration: none;
                font-weight: 600;
            }}
            a:hover {{
                text-decoration: underline;
                color: #2980b9;
            }}
            code {{
                background-color: #f8f9fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', 'Consolas', monospace;
                color: #e74c3c;
                font-weight: 600;
            }}
            pre {{
                background-color: #2c3e50;
                color: #ecf0f1;
                padding: 20px;
                border-radius: 8px;
                overflow-x: auto;
                border-left: 5px solid #3498db;
            }}
            blockquote {{
                border-left: 5px solid #f39c12;
                padding-left: 20px;
                margin-left: 0;
                margin-right: 0;
                padding: 15px 20px;
                background-color: #fef5e7;
                font-style: italic;
                color: #555;
            }}
            hr {{
                border: none;
                border-top: 3px solid #3498db;
                margin: 40px 0;
                opacity: 0.5;
            }}
            ul, ol {{
                margin-left: 20px;
                line-height: 1.9;
            }}
            li {{
                margin-bottom: 10px;
            }}
            p {{
                margin-bottom: 15px;
                line-height: 1.8;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: 700;
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
        
        # 支持多个收件人（逗号或分号分隔）
        recipient_list = []
        for email in recipient_email.replace(';', ',').split(','):
            email = email.strip()
            if email:
                recipient_list.append(email)
        
        if not recipient_list:
            logger.error("未找到有效的收件人邮箱")
            return False
        
        logger.info(f"收件人列表: {', '.join(recipient_list)} (共 {len(recipient_list)} 个)")
        
        # 预生成 HTML（所有收件人共用）
        html_body = markdown_to_html(body_markdown)
        
        logger.info(f"正在发送邮件到 {len(recipient_list)} 个收件人...")
        
        # 为每个收件人单独建立连接和发送（避免同一会话中的响应混淆）
        failed_recipients = []
        
        for idx, recipient in enumerate(recipient_list, 1):
            server = None
            try:
                logger.info(f"  [{idx}/{len(recipient_list)}] 正在发送到: {recipient}")
                
                # 为每个收件人创建独立的邮件对象
                msg = MIMEMultipart('alternative')
                msg['From'] = f'BioRxiv <{sender_email}>'
                msg['To'] = recipient
                msg['Subject'] = Header(subject, 'utf-8')
                
                # 添加纯文本版本（作为备用）
                text_part = MIMEText(body_markdown, 'plain', 'utf-8')
                msg.attach(text_part)
                
                # 添加 HTML 版本
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
                
                # 建立独立的 SMTP 连接
                if smtp_port == 465:
                    server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
                else:
                    server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                
                # 登录并发送
                server.login(sender_email, smtp_password)
                server.sendmail(sender_email, [recipient], msg.as_string())
                server.quit()
                
                logger.info(f"      ✅ 成功")
                
            except Exception as e:
                logger.error(f"      ❌ 失败: {e}")
                failed_recipients.append(recipient)
            finally:
                # 确保连接关闭
                if server:
                    try:
                        server.quit()
                    except:
                        pass
        
        # 汇总结果
        if failed_recipients:
            logger.warning(f"⚠️ 部分邮件发送失败 ({len(failed_recipients)}/{len(recipient_list)}): {', '.join(failed_recipients)}")
            # 只要有一个成功就返回 True
            return len(failed_recipients) < len(recipient_list)
        else:
            logger.info(f"✅ 邮件发送成功到所有 {len(recipient_list)} 个收件人")
            return True
        
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

