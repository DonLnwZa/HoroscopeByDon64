// Empirical Stress Test Harness for Tarot Card Grid & Form Submit Logic (Milestone M2 Frontend)

class TarotFormSimulator {
    constructor() {
        this.loading = false;
        this.results = null;
        this.formData = {
            full_name: "สมชาย ดวงดี",
            birth_date: "1995-08-15",
            birth_time: "06:00",
            birth_province: "กรุงเทพมหานคร"
        };
        this.selectedTarotCards = [];
    }

    handleCardClick(cardIndex) {
        if (this.selectedTarotCards.includes(cardIndex)) {
            this.selectedTarotCards = this.selectedTarotCards.filter(id => id !== cardIndex);
        } else if (this.selectedTarotCards.length < 10) {
            this.selectedTarotCards = [...this.selectedTarotCards, cardIndex];
        }
    }

    getCounterText() {
        return `เลือกไพ่แล้ว ${this.selectedTarotCards.length} / 10 ใบ`;
    }

    isSubmitDisabled() {
        return this.loading || this.selectedTarotCards.length !== 10;
    }

    getSubmitButtonText() {
        if (this.loading) {
            return "กำลังเปิดประตูแห่งดวงดาว...";
        }
        if (this.selectedTarotCards.length !== 10) {
            return `กรุณาเลือกไพ่ทาโรต์ให้ครบ 10 ใบ (เลือกแล้ว ${this.selectedTarotCards.length}/10)`;
        }
        return "ค้นหาเลขมงคล 🔮";
    }

    createPayload() {
        if (this.selectedTarotCards.length !== 10) {
            throw new Error("Validation Error: Cannot submit without exactly 10 cards");
        }
        return {
            full_name: this.formData.full_name,
            birth_date: this.formData.birth_date,
            birth_time: this.formData.birth_time,
            birth_province: this.formData.birth_province,
            selected_tarot_cards: this.selectedTarotCards
        };
    }
}

function runEmpiricalTests() {
    const results = [];
    
    // Test Case 1: Selecting 0 cards, 1 card, 9 cards, 10 cards, and 11+ cards
    {
        const sim = new TarotFormSimulator();
        
        // 0 cards
        const tc1_0 = sim.selectedTarotCards.length === 0;
        
        // 1 card
        sim.handleCardClick(0);
        const tc1_1 = sim.selectedTarotCards.length === 1 && sim.selectedTarotCards[0] === 0;
        
        // 9 cards total (select indices 1..8)
        for (let i = 1; i <= 8; i++) {
            sim.handleCardClick(i);
        }
        const tc1_9 = sim.selectedTarotCards.length === 9;
        
        // 10 cards total (select index 9)
        sim.handleCardClick(9);
        const tc1_10 = sim.selectedTarotCards.length === 10;
        
        // 11th card attempt (select index 10)
        sim.handleCardClick(10);
        const tc1_11 = sim.selectedTarotCards.length === 10 && !sim.selectedTarotCards.includes(10);
        
        results.push({
            name: "1. Card selection boundary states (0, 1, 9, 10, 11+ cards capped at 10)",
            pass: tc1_0 && tc1_1 && tc1_9 && tc1_10 && tc1_11,
            details: { tc1_0, tc1_1, tc1_9, tc1_10, tc1_11, finalLength: sim.selectedTarotCards.length }
        });
    }

    // Test Case 2: Counter text format strictly matches `เลือกไพ่แล้ว X / 10 ใบ`
    {
        const sim = new TarotFormSimulator();
        const expected0 = "เลือกไพ่แล้ว 0 / 10 ใบ";
        const pass0 = sim.getCounterText() === expected0;
        
        sim.handleCardClick(5);
        const expected1 = "เลือกไพ่แล้ว 1 / 10 ใบ";
        const pass1 = sim.getCounterText() === expected1;
        
        for (let i = 0; i < 8; i++) sim.handleCardClick(i); // cards 0..7 + 5 = 9 cards
        const expected9 = "เลือกไพ่แล้ว 9 / 10 ใบ";
        const pass9 = sim.getCounterText() === expected9;
        
        sim.handleCardClick(8); // 10 cards
        const expected10 = "เลือกไพ่แล้ว 10 / 10 ใบ";
        const pass10 = sim.getCounterText() === expected10;

        results.push({
            name: "2. Counter text format strictly matches `เลือกไพ่แล้ว X / 10 ใบ`",
            pass: pass0 && pass1 && pass9 && pass10,
            details: { pass0, pass1, pass9, pass10, text10: sim.getCounterText() }
        });
    }

    // Test Case 3: Submit button disabled when X != 10 and enabled ONLY when X == 10
    {
        const sim = new TarotFormSimulator();
        
        const dis0 = sim.isSubmitDisabled() === true;
        
        sim.handleCardClick(0);
        const dis1 = sim.isSubmitDisabled() === true;
        
        for (let i = 1; i <= 8; i++) sim.handleCardClick(i);
        const dis9 = sim.isSubmitDisabled() === true;
        
        sim.handleCardClick(9);
        const en10 = sim.isSubmitDisabled() === false;
        const text10 = sim.getSubmitButtonText() === "ค้นหาเลขมงคล 🔮";
        
        // Deselect one card -> X becomes 9
        sim.handleCardClick(9);
        const disAfterDeselect = sim.isSubmitDisabled() === true;
        
        results.push({
            name: "3. Submit button disabled when X != 10 and enabled ONLY when X == 10",
            pass: dis0 && dis1 && dis9 && en10 && text10 && disAfterDeselect,
            details: { dis0, dis1, dis9, en10, text10, disAfterDeselect }
        });
    }

    // Test Case 4: Toggling card selection (select and deselect) works cleanly
    {
        const sim = new TarotFormSimulator();
        
        // Select card index 42
        sim.handleCardClick(42);
        const has42 = sim.selectedTarotCards.includes(42);
        
        // Deselect card index 42
        sim.handleCardClick(42);
        const notHas42 = !sim.selectedTarotCards.includes(42) && sim.selectedTarotCards.length === 0;
        
        // Select cards 10, 20, 30
        sim.handleCardClick(10);
        sim.handleCardClick(20);
        sim.handleCardClick(30);
        
        // Deselect card 20
        sim.handleCardClick(20);
        const arrayEquals10_30 = sim.selectedTarotCards.length === 2 && 
            sim.selectedTarotCards[0] === 10 && 
            sim.selectedTarotCards[1] === 30;
            
        results.push({
            name: "4. Toggling card selection (select and deselect) works cleanly",
            pass: has42 && notHas42 && arrayEquals10_30,
            details: { has42, notHas42, arrayEquals10_30, cards: sim.selectedTarotCards }
        });
    }

    // Test Case 5: JSON payload sent to backend contains selected_tarot_cards array of 10 card indices (0..77)
    {
        const sim = new TarotFormSimulator();
        const selectedIndices = [0, 7, 15, 23, 31, 40, 48, 56, 64, 77];
        selectedIndices.forEach(id => sim.handleCardClick(id));
        
        const payload = sim.createPayload();
        const passKey = Array.isArray(payload.selected_tarot_cards);
        const passLen = payload.selected_tarot_cards.length === 10;
        const passValues = JSON.stringify(payload.selected_tarot_cards) === JSON.stringify(selectedIndices);
        const passRange = payload.selected_tarot_cards.every(idx => Number.isInteger(idx) && idx >= 0 && idx <= 77);

        results.push({
            name: "5. JSON payload contains `selected_tarot_cards` array of 10 card indices (0..77)",
            pass: passKey && passLen && passValues && passRange,
            details: { passKey, passLen, passValues, passRange, payload }
        });
    }

    return results;
}

const testResults = runEmpiricalTests();
console.log("=== EMPIRICAL STRESS TEST RESULTS ===");
testResults.forEach(r => {
    console.log(`[${r.pass ? 'PASS' : 'FAIL'}] ${r.name}`);
    console.log(` Details:`, JSON.stringify(r.details));
});
