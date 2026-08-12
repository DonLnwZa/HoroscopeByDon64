const { useState, useEffect } = React;
const { motion, AnimatePresence } = window.Motion || { motion: { div: 'div' }, AnimatePresence: ({ children }) => children };

function App() {
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [formData, setFormData] = useState({
        full_name: "สมชาย ดวงดี",
        birth_date: "1995-08-15",
        birth_time: "06:00",
        birth_province: "กรุงเทพมหานคร"
    });
    const [selectedTarotCards, setSelectedTarotCards] = useState([]);

    const handleCardClick = (cardIndex) => {
        if (selectedTarotCards.includes(cardIndex)) {
            setSelectedTarotCards(selectedTarotCards.filter(id => id !== cardIndex));
        } else if (selectedTarotCards.length < 10) {
            setSelectedTarotCards([...selectedTarotCards, cardIndex]);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (selectedTarotCards.length !== 10) {
            alert("กรุณาเลือกไพ่ทาโรต์ให้ครบ 10 ใบ ก่อนทำนาย");
            return;
        }
        setLoading(true);
        
        try {
            const payload = {
                full_name: formData.full_name,
                birth_date: formData.birth_date,
                birth_time: formData.birth_time,
                birth_province: formData.birth_province,
                selected_tarot_cards: selectedTarotCards
            };
            const res = await fetch("http://localhost:5000/api/divine", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            setResults(data);
        } catch (err) {
            console.error(err);
            alert("ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ กรุณาตรวจสอบว่า Backend ทำงานอยู่");
        } finally {
            setLoading(false);
        }
    };

    const renderHeatBadge = (category, numStr) => {
        if (!results?.heat_index?.[category]) return null;
        const item = results.heat_index[category].find(h => String(h.number) === String(numStr));
        if (!item) return null;

        let badgeClass = "heat-badge cold";
        let text = `❄️ หายาก (ชนะ ${item.win_count} ครั้ง)`;
        if (item.level === "HOT") {
            badgeClass = "heat-badge hot";
            text = `🔥 ร้อนแรง (ชนะ ${item.win_count} ครั้ง)`;
        } else if (item.level === "WARM") {
            badgeClass = "heat-badge warm";
            text = `⚡ ปานกลาง (ชนะ ${item.win_count} ครั้ง)`;
        }

        return (
            <span className={badgeClass} title={`สถิติผลหวยย้อนหลัง 1 ปี: ชนะ ${item.win_count} ครั้ง`}>
                {text}
            </span>
        );
    };

    const renderOrigins = (numStr) => {
        const origins = results?.number_origins?.[numStr];
        if (!origins || origins.length === 0) return null;
        return (
            <div className="origin-tags-group">
                <span className="origin-label">📍 ที่มา:</span>
                {origins.map((org, i) => (
                    <span key={i} className="origin-tag">
                        {org}
                    </span>
                ))}
            </div>
        );
    };

    return (
        <div className="app-container">
            <motion.div 
                className="header"
                initial={{ opacity: 0, y: -50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1 }}
            >
                <h1 className="gold-text">✨ Omni-Oracle ✨</h1>
                <p>สุดยอดระบบพยากรณ์ศาสตร์ 4 แขนง เพื่อค้นหาเลขมงคลของคุณ</p>
            </motion.div>

            {!results ? (
                <motion.div 
                    className="glass-card"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                >
                    <form onSubmit={handleSubmit}>
                        <div className="form-grid">
                            <div className="form-group full-width">
                                <label htmlFor="full_name">ชื่อ-นามสกุล</label>
                                <input 
                                    id="full_name"
                                    aria-label="ชื่อ-นามสกุล"
                                    type="text" 
                                    value={formData.full_name} 
                                    onChange={e => setFormData({...formData, full_name: e.target.value})} 
                                    required 
                                    placeholder="เช่น สมชาย ดวงดี" 
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="birth_date">วันเดือนปีเกิด (สากล)</label>
                                <input 
                                    id="birth_date"
                                    aria-label="วันเกิด"
                                    type="date" 
                                    value={formData.birth_date} 
                                    onChange={e => setFormData({...formData, birth_date: e.target.value})} 
                                    required 
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="birth_time">เวลาเกิด (ตัดรอบ 06:00 น. แบบไทย)</label>
                                <input 
                                    id="birth_time"
                                    name="birth_time"
                                    aria-label="เวลาเกิด"
                                    type="time" 
                                    value={formData.birth_time} 
                                    onChange={e => setFormData({...formData, birth_time: e.target.value})} 
                                    required 
                                />
                            </div>
                            <div className="form-group full-width">
                                <label htmlFor="birth_province">จังหวัดเกิด</label>
                                <select 
                                    id="birth_province"
                                    aria-label="จังหวัดเกิด"
                                    value={formData.birth_province}
                                    onChange={e => setFormData({...formData, birth_province: e.target.value})}
                                >
                                    <option value="กรุงเทพมหานคร">กรุงเทพมหานคร</option>
                                    <option value="เชียงใหม่">เชียงใหม่</option>
                                    <option value="ขอนแก่น">ขอนแก่น</option>
                                    <option value="ภูเก็ต">ภูเก็ต</option>
                                    <option value="ชลบุรี">ชลบุรี</option>
                                </select>
                            </div>
                        </div>

                        {/* R2 Tarot Card Deck Grid */}
                        <div className="tarot-section">
                            <h3 className="gold-text">🃏 เลือกไพ่ทาโรต์มงคล 10 ใบ</h3>
                            <p className="card-counter" aria-label="card-counter">
                                เลือกไพ่แล้ว {selectedTarotCards.length} / 10 ใบ
                            </p>
                            <div className="tarot-deck-grid">
                                {[...Array(78)].map((_, index) => {
                                    const isSelected = selectedTarotCards.includes(index);
                                    const selectOrder = selectedTarotCards.indexOf(index) + 1;
                                    return (
                                        <div
                                            key={index}
                                            data-testid={`tarot-card-${index}`}
                                            className={`tarot-card-facedown ${isSelected ? 'selected' : ''}`}
                                            onClick={() => handleCardClick(index)}
                                            title={`ไพ่ใบที่ ${index + 1}`}
                                        >
                                            {isSelected ? (
                                                <span className="card-order-badge">#{selectOrder}</span>
                                            ) : (
                                                <span className="card-back-pattern">🔮</span>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        <button 
                            type="submit" 
                            className="btn-primary" 
                            disabled={loading || selectedTarotCards.length !== 10} 
                            style={{width: '100%'}}
                        >
                            {loading 
                                ? "กำลังเปิดประตูแห่งดวงดาว..." 
                                : selectedTarotCards.length !== 10 
                                    ? `กรุณาเลือกไพ่ทาโรต์ให้ครบ 10 ใบ (เลือกแล้ว ${selectedTarotCards.length}/10)` 
                                    : "ค้นหาเลขมงคล 🔮"}
                        </button>
                    </form>
                </motion.div>
            ) : (
                <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1 }}
                >
                    {/* R1 Auto-Calculated Thai Lunar Calendar Output Card */}
                    {results.chart?.lunar_calendar && (
                        <motion.div 
                            className="glass-card lunar-card"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5 }}
                        >
                            <h3 className="gold-text">🌙 ปฏิทินจันทรคติไทย (คำนวณอัตโนมัติ)</h3>
                            <div className="lunar-info-grid">
                                <div className="lunar-item">
                                    <span className="lunar-label">วันเกิดตามสัปดาห์</span>
                                    <span className="lunar-val">{results.chart.lunar_calendar.day_of_week}</span>
                                </div>
                                <div className="lunar-item">
                                    <span className="lunar-label">เดือนจันทรคติ</span>
                                    <span className="lunar-val">เดือน {results.chart.lunar_calendar.lunar_month}</span>
                                </div>
                                <div className="lunar-item">
                                    <span className="lunar-label">ปีนักษัตร</span>
                                    <span className="lunar-val">ปี{results.chart.lunar_calendar.zodiac_year}</span>
                                </div>
                            </div>
                            <p className="cutoff-note">
                                {results.chart.lunar_calendar.cutoff_applied 
                                    ? "🌅 คำนวณโดยใช้กฎตัดรอบวันใหม่เวลา 06:00 น. ตามหลักโหราศาสตร์ไทย" 
                                    : "☀️ เวลาเกิดหลัง 06:00 น. ตรงตามวันทางสากล"}
                            </p>
                        </motion.div>
                    )}

                    <motion.div 
                        className="glass-card lucky-numbers"
                        initial={{ scale: 0.95 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", bounce: 0.4 }}
                    >
                        <h2 className="gold-text">🎯 เลขเด็ดมงคลของคุณงวดนี้</h2>

                        {/* R3 & R4: 2-Digit Numbers */}
                        <div className="number-section">
                            <h3 className="section-title">เลข 2 ตัว (เลขเด็ดหลัก)</h3>
                            <div className="number-cards-grid">
                                {(results.lucky_numbers?.two_digit || results.lucky_numbers?.two_digits || []).map((num, idx) => (
                                    <div key={idx} className="number-card-row">
                                        <div className="number-card-header">
                                            <span className="number-value gold-text">{num}</span>
                                            {renderHeatBadge("two_digit", num)}
                                        </div>
                                        {renderOrigins(num)}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* R3 & R4: 3-Digit Numbers */}
                        <div className="number-section" style={{marginTop: '1.5rem'}}>
                            <h3 className="section-title">เลข 3 ตัว</h3>
                            <div className="number-cards-grid">
                                {(results.lucky_numbers?.three_digit || results.lucky_numbers?.three_digits || []).map((num, idx) => (
                                    <div key={idx} className="number-card-row">
                                        <div className="number-card-header">
                                            <span className="number-value gold-text">{num}</span>
                                            {renderHeatBadge("three_digit", num)}
                                        </div>
                                        {renderOrigins(num)}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* R3 & R4: 6-Digit Numbers */}
                        <div className="number-section" style={{marginTop: '1.5rem'}}>
                            <h3 className="section-title">เลข 6 ตัว (รางวัลที่ 1)</h3>
                            <div className="number-cards-grid">
                                {(results.lucky_numbers?.six_digit || results.lucky_numbers?.six_digits || []).map((num, idx) => (
                                    <div key={idx} className="number-card-row">
                                        <div className="number-card-header">
                                            <span className="number-value gold-text" style={{fontSize: '2rem'}}>{num}</span>
                                            {renderHeatBadge("six_digit", num)}
                                        </div>
                                        {renderOrigins(num)}
                                    </div>
                                ))}
                            </div>
                        </div>
                        
                        <hr style={{borderColor: 'rgba(255,215,0,0.3)', margin: '2rem 0'}}/>
                        <p style={{fontSize: '1.2rem', lineHeight: '1.6', textAlign: 'left'}}>{results.synthesis}</p>
                        <p style={{fontSize: '0.8rem', opacity: 0.7, marginTop: '1rem', textAlign: 'left'}}>⚠️ {results.disclaimer}</p>
                        
                        <button onClick={() => { setResults(null); setSelectedTarotCards([]); }} className="btn-primary" style={{marginTop: '2rem'}}>
                            วิเคราะห์ดวงชะตาใหม่
                        </button>
                    </motion.div>
                </motion.div>
            )}
        </div>
    );
}

if (typeof ReactDOM !== 'undefined' && document.getElementById('root')) {
    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
}
