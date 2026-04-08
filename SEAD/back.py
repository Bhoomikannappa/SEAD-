# back.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class SecurityAnalyzer:
    """Security Analysis Module"""
    
    def __init__(self):
        self.security_patterns = {
            'hardcoded_passwords': {
                'pattern': r'(password|passwd|pwd)\s*=\s*["\']([^"\']+)["\']',
                'severity': 'high',
                'description': 'Hardcoded password detected'
            },
            'sql_injection': {
                'pattern': r'(execute|executeQuery|exec)\s*\(.*?\+\s*.*?\)',
                'severity': 'critical',
                'description': 'Potential SQL injection vulnerability'
            },
            'eval_usage': {
                'pattern': r'\beval\s*\(',
                'severity': 'high',
                'description': 'Use of eval() function - potential code injection risk'
            },
            'weak_encryption': {
                'pattern': r'(md5|sha1)\s*\(',
                'severity': 'medium',
                'description': 'Weak encryption algorithm detected'
            },
            'unvalidated_input': {
                'pattern': r'(input|raw_input)\s*\(\s*\)',
                'severity': 'medium',
                'description': 'Unvalidated user input'
            }
        }
    
    def analyze(self, code):
        """Analyze code for security vulnerabilities"""
        findings = []
        security_score = 100
        
        for vuln_name, vuln_info in self.security_patterns.items():
            matches = re.findall(vuln_info['pattern'], code, re.IGNORECASE)
            if matches:
                findings.append({
                    'type': vuln_name,
                    'severity': vuln_info['severity'],
                    'description': vuln_info['description'],
                    'occurrences': len(matches)
                })
                
                # Reduce score based on severity
                severity_weights = {'critical': 30, 'high': 20, 'medium': 10, 'low': 5}
                security_score -= severity_weights.get(vuln_info['severity'], 5) * min(len(matches), 3)
        
        return {
            'score': max(0, security_score),
            'findings': findings,
            'summary': self._generate_summary(findings)
        }
    
    def _generate_summary(self, findings):
        """Generate summary of findings"""
        if not findings:
            return "No security issues detected. Code appears secure."
        
        critical = sum(1 for f in findings if f['severity'] == 'critical')
        high = sum(1 for f in findings if f['severity'] == 'high')
        medium = sum(1 for f in findings if f['severity'] == 'medium')
        
        return f"Found {critical} critical, {high} high, and {medium} medium severity security issues."


class PrivacyAnalyzer:
    """Privacy Analysis Module"""
    
    def __init__(self):
        self.sensitive_patterns = {
            'email': {
                'pattern': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'category': 'PII',
                'severity': 'high',
                'description': 'Email addresses detected'
            },
            'phone': {
                'pattern': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                'category': 'PII',
                'severity': 'high',
                'description': 'Phone numbers detected'
            },
            'api_key': {
                'pattern': r'(api[_-]?key|apikey|token)\s*=\s*["\']([^"\']+)["\']',
                'category': 'Credential',
                'severity': 'critical',
                'description': 'API keys exposed in code'
            }
        }
        
        self.privacy_practices = {
            'data_collection': {
                'keywords': ['collect', 'gather', 'store', 'save'],
                'required': True
            },
            'data_encryption': {
                'keywords': ['encrypt', 'decrypt', 'cipher'],
                'required': True
            },
            'user_consent': {
                'keywords': ['consent', 'agree', 'opt-in'],
                'required': True
            }
        }
    
    def analyze(self, code):
        """Analyze code for privacy issues"""
        findings = []
        privacy_score = 100
        detected_pii = []
        
        # Check for sensitive data exposure
        for pattern_name, pattern_info in self.sensitive_patterns.items():
            matches = re.findall(pattern_info['pattern'], code, re.IGNORECASE)
            if matches:
                findings.append({
                    'type': pattern_name,
                    'category': pattern_info['category'],
                    'severity': pattern_info['severity'],
                    'description': pattern_info['description'],
                    'occurrences': len(matches)
                })
                
                detected_pii.extend(matches)
                severity_weights = {'critical': 35, 'high': 20, 'medium': 10}
                privacy_score -= severity_weights.get(pattern_info['severity'], 10) * min(len(matches), 3)
        
        # Check privacy practices
        for practice, info in self.privacy_practices.items():
            has_practice = any(keyword in code.lower() for keyword in info['keywords'])
            if not has_practice:
                findings.append({
                    'type': f'missing_{practice}',
                    'severity': 'high',
                    'description': f'Missing {practice.replace("_", " ")} implementation',
                    'occurrences': 0
                })
                privacy_score -= 20
        
        return {
            'score': max(0, privacy_score),
            'findings': findings,
            'detected_pii': list(set(detected_pii[:5])),
            'summary': self._generate_summary(findings)
        }
    
    def _generate_summary(self, findings):
        """Generate privacy summary"""
        if not findings:
            return "Good privacy practices detected. No privacy violations found."
        
        critical = sum(1 for f in findings if f['severity'] == 'critical')
        high = sum(1 for f in findings if f['severity'] == 'high')
        
        return f"Found {critical} critical and {high} high severity privacy concerns."


class EthicalAnalyzer:
    """Ethical Decision Engine"""
    
    def __init__(self):
        pass
    
    def analyze(self, security_result, privacy_result):
        """Make ethical decision based on security and privacy analysis"""
        total_score = (security_result['score'] + privacy_result['score']) / 2
        critical_issues = []
        
        # Check for critical issues
        for finding in security_result['findings']:
            if finding['severity'] == 'critical':
                critical_issues.append(f"Security: {finding['description']}")
        
        for finding in privacy_result['findings']:
            if finding['severity'] == 'critical':
                critical_issues.append(f"Privacy: {finding['description']}")
        
        # Make ethical decision
        if total_score >= 80 and len(critical_issues) == 0:
            decision = 'APPROVE'
            confidence = 'high'
            reason = 'Code meets all security and privacy requirements with no critical issues.'
        elif total_score >= 60:
            decision = 'REVIEW'
            confidence = 'medium'
            reason = f'Code needs review. Score: {total_score:.1f}/100. {len(critical_issues)} critical issues found.'
        else:
            decision = 'REJECT'
            confidence = 'high'
            reason = f'Code does not meet minimum requirements. Score: {total_score:.1f}/100. Critical issues require immediate attention.'
        
        return {
            'decision': decision,
            'confidence': confidence,
            'score': total_score,
            'critical_issues': critical_issues,
            'recommendations': self._generate_recommendations(security_result, privacy_result),
            'summary': self._generate_ethical_summary(decision, total_score, critical_issues)
        }
    
    def _generate_recommendations(self, security_result, privacy_result):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Security recommendations
        for finding in security_result['findings']:
            if finding['severity'] in ['critical', 'high']:
                if 'password' in finding['type']:
                    recommendations.append("Use environment variables or secure secret management for credentials")
                elif 'sql' in finding['type']:
                    recommendations.append("Use parameterized queries or ORM to prevent SQL injection")
                elif 'eval' in finding['type']:
                    recommendations.append("Avoid using eval() - consider safer alternatives")
        
        # Privacy recommendations
        for finding in privacy_result['findings']:
            if 'PII' in finding.get('category', ''):
                recommendations.append("Implement data encryption for sensitive personal information")
            elif 'missing_data_collection' in finding['type']:
                recommendations.append("Add data collection policy and user consent mechanism")
        
        return recommendations[:5]
    
    def _generate_ethical_summary(self, decision, score, critical_issues):
        """Generate ethical summary"""
        if decision == 'APPROVE':
            return f"✅ Ethical Decision: APPROVED - Code meets ethical standards with a score of {score:.1f}/100"
        elif decision == 'REVIEW':
            return f"⚠️ Ethical Decision: REVIEW REQUIRED - Score: {score:.1f}/100. {len(critical_issues)} issues need review"
        else:
            return f"❌ Ethical Decision: REJECTED - Score: {score:.1f}/100. Critical ethical violations detected"


@app.route('/analyze', methods=['POST'])
def analyze_code():
    """
    API endpoint to analyze code for security, privacy, and ethical issues
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
        
        code = data['code']
        
        # Initialize analyzers
        security_analyzer = SecurityAnalyzer()
        privacy_analyzer = PrivacyAnalyzer()
        ethical_analyzer = EthicalAnalyzer()
        
        # Perform analyses
        security_result = security_analyzer.analyze(code)
        privacy_result = privacy_analyzer.analyze(code)
        ethical_result = ethical_analyzer.analyze(security_result, privacy_result)
        
        # Prepare response
        response = {
            'security': {
                'report': security_result,
                'formatted_output': format_security_output(security_result)
            },
            'privacy': {
                'report': privacy_result,
                'formatted_output': format_privacy_output(privacy_result)
            },
            'ethical': {
                'report': ethical_result,
                'formatted_output': format_ethical_output(ethical_result)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def format_security_output(result):
    """Format security analysis for display"""
    output = f"🔒 Security Analysis Report\n"
    output += f"Security Score: {result['score']}/100\n\n"
    
    if not result['findings']:
        output += "✅ No security vulnerabilities detected!\n"
    else:
        output += f"⚠️ Found {len(result['findings'])} security issues:\n\n"
        for finding in result['findings']:
            severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
            output += f"{severity_icon.get(finding['severity'], '⚪')} {finding['severity'].upper()}: {finding['description']}\n"
            output += f"   Occurrences: {finding['occurrences']}\n\n"
    
    output += f"\n{result['summary']}"
    return output


def format_privacy_output(result):
    """Format privacy analysis for display"""
    output = f"🔐 Privacy Analysis Report\n"
    output += f"Privacy Score: {result['score']}/100\n\n"
    
    if result['detected_pii']:
        output += f"📋 Detected PII/Sensitive Data:\n"
        for pii in result['detected_pii']:
            output += f"   • {pii}\n"
        output += "\n"
    
    if not result['findings']:
        output += "✅ Good privacy practices detected!\n"
    else:
        output += f"⚠️ Found {len(result['findings'])} privacy concerns:\n\n"
        for finding in result['findings']:
            severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
            output += f"{severity_icon.get(finding['severity'], '⚪')} {finding['severity'].upper()}: {finding['description']}\n\n"
    
    output += f"\n{result['summary']}"
    return output


def format_ethical_output(result):
    """Format ethical decision for display"""
    output = f"⚖️ Ethical Decision Report\n"
    output += f"Decision: {result['decision']}\n"
    output += f"Confidence: {result['confidence']}\n"
    output += f"Overall Score: {result['score']:.1f}/100\n\n"
    
    if result['critical_issues']:
        output += f"🚨 Critical Issues Found:\n"
        for issue in result['critical_issues']:
            output += f"   • {issue}\n"
        output += "\n"
    
    if result['recommendations']:
        output += f"📝 Recommendations:\n"
        for rec in result['recommendations']:
            output += f"   • {rec}\n"
        output += "\n"
    
    output += f"\n{result['summary']}"
    return output


if __name__ == '__main__':
    print("🚀 Starting Ethical Software Checker Backend...")
    print("📡 Server running at http://127.0.0.1:5000")
    print("🔍 API endpoint: http://127.0.0.1:5000/analyze")
    print("-" * 50)
    app.run(debug=True, port=5000, host='127.0.0.1')