"""
静态检查模块
使用Python库对HTML、CSS和JavaScript代码进行静态检查
"""

import html5lib
import cssutils
import esprima
import logging
from typing import Dict, List, Any
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置cssutils日志级别，避免过多的警告信息
cssutils.log.setLevel(logging.ERROR)

class StaticChecker:
    """静态检查器类"""
    
    def __init__(self):
        """初始化静态检查器"""
        logger.info("StaticChecker initialized")
    
    def check_html(self, html_code: str) -> Dict[str, Any]:
        """
        检查HTML代码
        
        Args:
            html_code: HTML代码字符串
            
        Returns:
            检查结果字典
        """
        errors = []
        warnings = []
        
        try:
            # 使用html5lib解析HTML代码
            parser = html5lib.HTMLParser(strict=True)
            parser.parse(html_code)
        except html5lib.html5parser.ParseError as e:
            # 提取错误信息
            error_msg = str(e)
            line_number = self._extract_line_number(error_msg)
            errors.append({
                "line": line_number,
                "column": 0,
                "message": f"HTML解析错误: {error_msg}",
                "severity": "error"
            })
        except Exception as e:
            errors.append({
                "line": 0,
                "column": 0,
                "message": f"HTML检查异常: {str(e)}",
                "severity": "error"
            })
        
        # 检查未闭合的标签
        unclosed_tags = self._check_unclosed_tags(html_code)
        for tag in unclosed_tags:
            warnings.append({
                "line": tag.get("line", 0),
                "column": tag.get("column", 0),
                "message": f"未闭合的标签: {tag['tag']}",
                "severity": "warning"
            })
        
        return {
            "status": "success" if not errors else "error",
            "errors": errors,
            "warnings": warnings
        }
    
    def check_css(self, css_code: str) -> Dict[str, Any]:
        """
        检查CSS代码
        
        Args:
            css_code: CSS代码字符串
            
        Returns:
            检查结果字典
        """
        errors = []
        warnings = []
        
        try:
            # 使用cssutils解析CSS代码
            sheet = cssutils.parseString(css_code)
            
            # 检查CSS验证错误
            for error in sheet.errors:
                errors.append({
                    "line": error.line,
                    "column": error.col,
                    "message": error.message,
                    "severity": "error"
                })
                
            # 检查CSS验证警告
            for warning in sheet.warnings:
                warnings.append({
                    "line": warning.line,
                    "column": warning.col,
                    "message": warning.message,
                    "severity": "warning"
                })
        except Exception as e:
            errors.append({
                "line": 0,
                "column": 0,
                "message": f"CSS检查异常: {str(e)}",
                "severity": "error"
            })
        
        return {
            "status": "success" if not errors else "error",
            "errors": errors,
            "warnings": warnings
        }
    
    def check_js(self, js_code: str) -> Dict[str, Any]:
        """
        检查JavaScript代码
        
        Args:
            js_code: JavaScript代码字符串
            
        Returns:
            检查结果字典
        """
        errors = []
        warnings = []
        
        try:
            # 使用esprima解析JavaScript代码
            esprima.parseScript(js_code)
        except esprima.Error as e:
            # 提取错误信息
            error_msg = str(e)
            line_number = self._extract_line_number(error_msg)
            errors.append({
                "line": line_number,
                "column": 0,
                "message": f"JavaScript语法错误: {error_msg}",
                "severity": "error"
            })
        except Exception as e:
            errors.append({
                "line": 0,
                "column": 0,
                "message": f"JavaScript检查异常: {str(e)}",
                "severity": "error"
            })
        
        return {
            "status": "success" if not errors else "error",
            "errors": errors,
            "warnings": warnings
        }
    
    def check_all(self, html_code: str, css_code: str = "", js_code: str = "") -> Dict[str, Any]:
        """
        检查所有代码（HTML、CSS、JavaScript）
        
        Args:
            html_code: HTML代码字符串
            css_code: CSS代码字符串
            js_code: JavaScript代码字符串
            
        Returns:
            检查结果字典
        """
        # 检查HTML
        html_result = self.check_html(html_code)
        
        # 检查CSS
        css_result = self.check_css(css_code)
        
        # 检查JavaScript
        js_result = self.check_js(js_code)
        
        # 合并结果
        all_errors = html_result["errors"] + css_result["errors"] + js_result["errors"]
        all_warnings = html_result["warnings"] + css_result["warnings"] + js_result["warnings"]
        
        return {
            "status": "success" if not all_errors else "error",
            "errors": all_errors,
            "warnings": all_warnings,
            "details": {
                "html": html_result,
                "css": css_result,
                "js": js_result
            }
        }
    
    def _extract_line_number(self, error_message: str) -> int:
        """
        从错误信息中提取行号
        
        Args:
            error_message: 错误信息字符串
            
        Returns:
            行号
        """
        # 尝试从错误信息中提取行号
        match = re.search(r'line\s*(\d+)', error_message, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        match = re.search(r':(\d+):', error_message)
        if match:
            return int(match.group(1))
            
        return 0
    
    def _check_unclosed_tags(self, html_code: str) -> List[Dict[str, Any]]:
        """
        检查未闭合的标签
        
        Args:
            html_code: HTML代码字符串
            
        Returns:
            未闭合标签列表
        """
        unclosed_tags = []
        # 简单的未闭合标签检查实现
        # 这里可以扩展更复杂的检查逻辑
        
        # 一些常见的自闭合标签
        self_closing_tags = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source']
        
        # 简单的标签匹配检查
        # 注意：这是一个简化的实现，实际应用中可能需要更复杂的解析
        lines = html_code.split('\n')
        for line_num, line in enumerate(lines, 1):
            # 查找开始标签
            start_tags = re.findall(r'<(\w+)(?:\s[^>]*)?>', line)
            for tag in start_tags:
                if tag not in self_closing_tags:
                    # 检查是否有对应的结束标签
                    end_tag_pattern = f'</{tag}>'
                    if end_tag_pattern not in html_code:
                        unclosed_tags.append({
                            "tag": tag,
                            "line": line_num,
                            "column": line.find(f'<{tag}') + 1
                        })
        
        return unclosed_tags

# 单例模式
_static_checker_instance = None

def get_static_checker() -> StaticChecker:
    """获取StaticChecker单例"""
    global _static_checker_instance
    if _static_checker_instance is None:
        _static_checker_instance = StaticChecker()
    return _static_checker_instance