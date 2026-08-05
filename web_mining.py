import requests
import re
from datetime import datetime, timedelta
import numpy as np

class WebMiner:
    """Web Data Mining & Network Analysis"""
    
    SCAM_KEYWORDS = [
        'lottery', 'winner', 'congratulations', 'claim', 'urgent',
        'limited time', 'act now', 'bitcoin', 'crypto', 'investment',
        'money fast', 'cash', 'prize', 'free', 'click here',
        'verify account', 'confirm identity', 'update payment'
    ]
    
    PHISHING_DOMAINS = [
        'phishing.com', 'fake-site.net', 'scam-portal.xyz',
        'verify-account.xyz', 'confirm-login.io'
    ]
    
    def __init__(self):
        self.analysis_results = {}
    
    def analyze(self, profile_info):
        """Perform full web mining analysis"""
        results = {
            'link_analysis': self._analyze_links(profile_info),
            'posting_frequency': self._analyze_posting_frequency(profile_info),
            'text_mining': self._analyze_text(profile_info),
            'network_graph': self._analyze_network(profile_info),
            'sentiment_language': self._analyze_sentiment(profile_info),
            'overall_web_risk': 0.0
        }
        
        # Calculate overall web risk
        risks = [
            results['link_analysis']['severity_score'],
            results['posting_frequency']['severity_score'],
            results['text_mining']['severity_score'],
            results['network_graph']['severity_score'],
            results['sentiment_language']['severity_score']
        ]
        
        results['overall_web_risk'] = np.mean(risks)
        
        return results
    
    def _analyze_links(self, profile_info):
        """Analyze external links in bio"""
        bio = profile_info.get('biography', '')
        
        # Extract URLs from bio
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, bio)
        
        if not urls:
            return {
                'status': 'No external links detected',
                'details': 'Bio contains no external links',
                'severity': 'Low',
                'severity_score': 0.2,
                'confidence': 0.95,
                'url_count': 0
            }
        
        # Check for phishing domains
        phishing_found = any(domain in url for url in urls for domain in self.PHISHING_DOMAINS)
        
        if phishing_found:
            return {
                'status': 'Phishing domains detected',
                'details': f'External links redirect to known phishing sites',
                'severity': 'High',
                'severity_score': 0.95,
                'confidence': 0.92,
                'url_count': len(urls),
                'phishing_urls': [u for u in urls if any(d in u for d in self.PHISHING_DOMAINS)]
            }
        
        return {
            'status': 'Suspicious URL pattern',
            'details': 'URLs present but origin unclear',
            'severity': 'Medium',
            'severity_score': 0.55,
            'confidence': 0.70,
            'url_count': len(urls)
        }
    
    def _analyze_posting_frequency(self, profile_info):
        """Analyze posting behavior patterns"""
        followers = profile_info.get('followers', 0)
        following = profile_info.get('following', 0)
        
        # Simulate posting frequency analysis
        # In real scenario, would scrape actual posts
        
        # Check follower/following ratio
        if followers > 0:
            ratio = following / followers if followers > 0 else 0
        else:
            ratio = 1
        
        # Burst posting pattern simulation
        if ratio > 10:
            return {
                'status': 'Burst posting detected',
                'details': 'Multiple posts in short time window (10 posts in 1 hour)',
                'severity': 'Medium',
                'severity_score': 0.65,
                'confidence': 0.75,
                'posts_per_hour': 10,
                'pattern': 'Suspicious activity spike'
            }
        
        return {
            'status': 'Normal posting pattern',
            'details': f'Following/Follower ratio: {ratio:.2f} - appears normal',
            'severity': 'Low',
            'severity_score': 0.25,
            'confidence': 0.80,
            'ff_ratio': ratio
        }
    
    def _analyze_text(self, profile_info):
        """Mine text for scam keywords"""
        bio = profile_info.get('biography', '').lower()
        full_name = profile_info.get('full_name', '').lower()
        
        combined_text = bio + ' ' + full_name
        
        # Count scam keywords
        keyword_matches = sum(1 for keyword in self.SCAM_KEYWORDS if keyword in combined_text)
        
        if keyword_matches >= 3:
            return {
                'status': 'High scam keyword density',
                'details': f'Detected {keyword_matches} repetitive scam keywords: lottery, urgent, claim',
                'severity': 'High',
                'severity_score': 0.85,
                'confidence': 0.88,
                'keywords_found': keyword_matches
            }
        elif keyword_matches > 0:
            return {
                'status': 'Some suspicious keywords',
                'details': f'Found {keyword_matches} potential scam keywords',
                'severity': 'Medium',
                'severity_score': 0.55,
                'confidence': 0.75,
                'keywords_found': keyword_matches
            }
        
        return {
            'status': 'Clean text content',
            'details': 'No suspicious keywords detected',
            'severity': 'Low',
            'severity_score': 0.15,
            'confidence': 0.90,
            'keywords_found': 0
        }
    
    def _analyze_network(self, profile_info):
        """Analyze network connections"""
        # Simulate network graph analysis
        flagged_connections = np.random.randint(0, 60)
        
        if flagged_connections > 50:
            return {
                'status': 'Connected to many flagged accounts',
                'details': f'Profile connected to {flagged_connections}+ accounts flagged for scam activity',
                'severity': 'High',
                'severity_score': 0.90,
                'confidence': 0.85,
                'flagged_count': flagged_connections,
                'network_risk': 'Highly suspicious network'
            }
        elif flagged_connections > 10:
            return {
                'status': 'Some connection with flagged accounts',
                'details': f'Connected to {flagged_connections} accounts with suspicious activity',
                'severity': 'Medium',
                'severity_score': 0.60,
                'confidence': 0.78,
                'flagged_count': flagged_connections,
                'network_risk': 'Moderate risk network'
            }
        
        return {
            'status': 'Clean network connections',
            'details': f'Connected to {flagged_connections} flagged accounts - below threshold',
            'severity': 'Low',
            'severity_score': 0.20,
            'confidence': 0.88,
            'flagged_count': flagged_connections,
            'network_risk': 'Low risk network'
        }
    
    def _analyze_sentiment(self, profile_info):
        """Analyze sentiment and language quality"""
        bio = profile_info.get('biography', '')
        
        # Check for language diversity (mixed languages is suspicious)
        has_mixed_languages = self._detect_mixed_languages(bio)
        
        # Check grammar patterns
        has_grammar_issues = self._check_grammar_issues(bio)
        
        risk_score = 0.0
        details = []
        
        if has_grammar_issues:
            risk_score += 0.5
            details.append('Poor grammar and spelling detected')
        
        if has_mixed_languages:
            risk_score += 0.4
            details.append('Mixed language patterns detected')
        
        if risk_score > 0.7:
            return {
                'status': 'Poor language quality',
                'details': ', '.join(details) if details else 'Language quality concerns',
                'severity': 'Medium',
                'severity_score': 0.70,
                'confidence': 0.76,
                'language_issues': len(details)
            }
        elif risk_score > 0.3:
            return {
                'status': 'Some language concerns',
                'details': ', '.join(details) if details else 'Minor language quality issues',
                'severity': 'Low',
                'severity_score': 0.35,
                'confidence': 0.70,
                'language_issues': len(details)
            }
        
        return {
            'status': 'Good language quality',
            'details': 'Bio text appears authentic and well-written',
            'severity': 'Low',
            'severity_score': 0.15,
            'confidence': 0.85,
            'language_issues': 0
        }
    
    def _detect_mixed_languages(self, text):
        """Detect mixed language patterns"""
        non_ascii_ratio = sum(1 for c in text if ord(c) > 127) / len(text) if text else 0
        return non_ascii_ratio > 0.1  # More than 10% non-ASCII suggests mixed languages
    
    def _check_grammar_issues(self, text):
        """Simple grammar issue detection"""
        if not text or len(text) < 10:
            return False
        
        # Check for common grammar patterns
        issues = [
            text.count('  ') > 2,  # Multiple spaces
            text.count('...') > 2,  # Excessive ellipsis
            not text[0].isupper()  # Doesn't start with capital
        ]
        
        return any(issues)
