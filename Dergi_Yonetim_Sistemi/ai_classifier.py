"""
Yapay Zeka Destekli Makale Sınıflandırma Modülü
Makalelerin özet ve anahtar kelimelerini analiz ederek uygun alan editörüne atar.
"""

import re
from typing import Optional, Dict, List


class AIArticleClassifier:
    """Makale sınıflandırma için yapay zeka sınıfı"""
    
    def __init__(self):
        # Alan bazlı anahtar kelime eşleştirmeleri
        self.field_keywords = {
            "Bilgisayar Mühendisliği": {
                "keywords": [
                    "yazılım", "software", "programlama", "programming", "algoritma", "algorithm",
                    "yapay zeka", "artificial intelligence", "ai", "machine learning", "makine öğrenmesi",
                    "veri bilimi", "data science", "big data", "büyük veri", "veri madenciliği",
                    "siber güvenlik", "cybersecurity", "bilgisayar ağları", "computer networks",
                    "veritabanı", "database", "yazılım mühendisliği", "software engineering",
                    "nesne yönelimli", "object oriented", "web", "mobil", "mobile",
                    "bulut", "cloud", "blockchain", "blokzincir", "iot", "nesnelerin interneti"
                ],
                "weight": 1.0
            },
            "Elektrik-Elektronik Mühendisliği": {
                "keywords": [
                    "elektrik", "electric", "elektronik", "electronic", "devre", "circuit",
                    "kontrol", "control", "sinyal işleme", "signal processing", "güç elektroniği",
                    "power electronics", "telekomünikasyon", "telecommunication", "anten",
                    "antenna", "mikroişlemci", "microprocessor", "gömülü sistem", "embedded",
                    "otomasyon", "automation", "sensör", "sensor", "aktüatör", "actuator",
                    "enerji sistemleri", "energy systems", "elektrik motorları", "electric motors"
                ],
                "weight": 1.0
            },
            "Makine Mühendisliği": {
                "keywords": [
                    "termodinamik", "thermodynamics", "akışkanlar mekaniği", "fluid mechanics",
                    "malzeme bilimi", "material science", "üretim", "manufacturing",
                    "robotik", "robotics", "otomasyon", "automation", "cad", "cam",
                    "tasarım", "design", "imalat", "production", "kalıp", "mold",
                    "makine elemanları", "machine elements", "vibrasyon", "vibration",
                    "ısı transferi", "heat transfer", "enerji", "energy"
                ],
                "weight": 1.0
            },
            "Endüstri Mühendisliği": {
                "keywords": [
                    "optimizasyon", "optimization", "yöneylem araştırması", "operations research",
                    "kalite yönetimi", "quality management", "tedarik zinciri", "supply chain",
                    "üretim planlama", "production planning", "stok yönetimi", "inventory",
                    "lojistik", "logistics", "proje yönetimi", "project management",
                    "karar analizi", "decision analysis", "simülasyon", "simulation",
                    "iş süreçleri", "business processes", "verimlilik", "efficiency"
                ],
                "weight": 1.0
            },
            "İnşaat Mühendisliği": {
                "keywords": [
                    "yapı", "structure", "beton", "concrete", "çelik", "steel",
                    "geoteknik", "geotechnical", "zemin", "soil", "ulaştırma", "transportation",
                    "su kaynakları", "water resources", "hidrolik", "hydraulics",
                    "yapı malzemeleri", "construction materials", "deprem", "earthquake",
                    "köprü", "bridge", "tünel", "tunnel", "baraj", "dam"
                ],
                "weight": 1.0
            },
            "Kimya Mühendisliği": {
                "keywords": [
                    "proses", "process", "reaksiyon", "reaction", "kimyasal", "chemical",
                    "ayırma", "separation", "distilasyon", "distillation", "ekstraksiyon",
                    "extraction", "polimer", "polymer", "katalizör", "catalyst",
                    "biyokimya", "biochemistry", "malzeme", "material", "endüstriyel"
                ],
                "weight": 1.0
            }
        }
    
    def classify_article(self, title: str, abstract_tr: str, abstract_en: str, 
                        keywords: str, field: Optional[str] = None) -> Optional[str]:
        """
        Makaleyi analiz ederek uygun alan editörünü belirler
        
        Args:
            title: Makale başlığı
            abstract_tr: Türkçe özet
            abstract_en: İngilizce özet
            keywords: Anahtar kelimeler
            field: Kullanıcının seçtiği alan (opsiyonel)
        
        Returns:
            Uygun alan editörü kullanıcı adı veya None
        """
        # Tüm metni birleştir ve küçük harfe çevir
        combined_text = f"{title} {abstract_tr} {abstract_en} {keywords}".lower()
        
        # Alan skorlarını hesapla
        field_scores = {}
        
        for field_name, field_data in self.field_keywords.items():
            score = 0
            keyword_list = field_data["keywords"]
            weight = field_data["weight"]
            
            # Her anahtar kelime için eşleşme sayısını hesapla
            for keyword in keyword_list:
                # Kelime sınırları ile eşleştirme (tam kelime)
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, combined_text))
                score += matches * weight
            
            # Kullanıcının seçtiği alan varsa bonus puan ver
            if field and field_name.lower() in field.lower():
                score += 10
            
            field_scores[field_name] = score
        
        # En yüksek skora sahip alanı bul
        if not field_scores or max(field_scores.values()) == 0:
            return None
        
        best_field = max(field_scores, key=field_scores.get)
        
        return best_field
    
    def assign_field_editor(self, field_name: str, available_editors: List[str], editor_expertise: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Belirlenen alan için uygun alan editörünü seçer
        
        Args:
            field_name: Belirlenen alan adı
            available_editors: Mevcut alan editörü kullanıcı adları listesi
            editor_expertise: Kullanıcı adı -> uzmanlık alanı eşleştirmesi (opsiyonel)
        
        Returns:
            Seçilen alan editörü kullanıcı adı veya None
        """
        if not available_editors:
            return None
        
        # Öncelik 1: Uzmanlık alanı tam eşleşen editörler
        if editor_expertise:
            for editor in available_editors:
                expertise = editor_expertise.get(editor)
                if expertise and expertise == field_name:
                    return editor
        
        # Öncelik 2: Kullanıcı adında alan adı geçen editörler
        field_lower = field_name.lower()
        for editor in available_editors:
            if any(keyword in editor.lower() for keyword in field_lower.split()):
                return editor
        
        # Öncelik 3: Uzmanlık alanı kısmen eşleşen editörler
        if editor_expertise:
            for editor in available_editors:
                expertise = editor_expertise.get(editor)
                if expertise:
                    # Alan adının bir kısmı uzmanlık alanında geçiyorsa
                    if any(word in expertise.lower() for word in field_lower.split()):
                        return editor
                    if any(word in field_lower for word in expertise.lower().split()):
                        return editor
        
        # Eşleşme yoksa ilk editörü döndür
        return available_editors[0]

