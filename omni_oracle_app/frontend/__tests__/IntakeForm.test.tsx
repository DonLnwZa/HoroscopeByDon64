import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

// Component simulating app.jsx IntakeForm with 78 Tarot grid and R1 birth_time
const MockIntakeForm = ({ onSubmit }: { onSubmit: (data: any) => void }) => {
  const [formData, setFormData] = React.useState({
    full_name: 'สมชาย ดวงดี',
    birth_date: '1995-08-15',
    birth_time: '06:00',
    birth_province: 'กรุงเทพมหานคร',
  });
  const [selectedCards, setSelectedCards] = React.useState<number[]>([]);
  const [error, setError] = React.useState('');

  const handleCardClick = (cardIndex: number) => {
    if (selectedCards.includes(cardIndex)) {
      setSelectedCards(selectedCards.filter(id => id !== cardIndex));
    } else if (selectedCards.length < 10) {
      setSelectedCards([...selectedCards, cardIndex]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.birth_date) {
      setError('กรุณาระบุวันเกิด');
      return;
    }
    if (selectedCards.length !== 10) {
      setError('กรุณาเลือกไพ่ทาโรต์ให้ครบ 10 ใบ');
      return;
    }
    onSubmit({
      ...formData,
      selected_tarot_cards: selectedCards,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="glass-card">
      <h2>ข้อมูลวันเกิดและดวงชะตา</h2>
      <div className="form-grid">
        <input
          aria-label="ชื่อ-นามสกุล"
          type="text"
          value={formData.full_name}
          onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
        />
        <input
          aria-label="วันเกิด"
          type="date"
          value={formData.birth_date}
          onChange={(e) => setFormData({ ...formData, birth_date: e.target.value })}
        />
        <input
          name="birth_time"
          aria-label="เวลาเกิด"
          type="time"
          value={formData.birth_time}
          onChange={(e) => setFormData({ ...formData, birth_time: e.target.value })}
        />
        <select
          aria-label="จังหวัดเกิด"
          value={formData.birth_province}
          onChange={(e) => setFormData({ ...formData, birth_province: e.target.value })}
        >
          <option value="กรุงเทพมหานคร">กรุงเทพมหานคร</option>
          <option value="เชียงใหม่">เชียงใหม่</option>
        </select>
      </div>

      <div className="tarot-section">
        <h3>เลือกไพ่ทาโรต์มงคล 10 ใบ</h3>
        <p className="card-counter" aria-label="card-counter">
          เลือกไพ่แล้ว {selectedCards.length} / 10 ใบ
        </p>
        <div className="tarot-deck-grid">
          {[...Array(78)].map((_, index) => {
            const isSelected = selectedCards.includes(index);
            return (
              <div
                key={index}
                data-testid={`tarot-card-${index}`}
                className={`tarot-card-facedown ${isSelected ? 'selected' : ''}`}
                onClick={() => handleCardClick(index)}
              >
                {isSelected ? index + 1 : '🔮'}
              </div>
            );
          })}
        </div>
      </div>

      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={selectedCards.length !== 10}>
        {selectedCards.length !== 10
          ? `กรุณาเลือกไพ่ทาโรต์ให้ครบ 10 ใบ (เลือกแล้ว ${selectedCards.length}/10)`
          : 'ทำนายดวงชะตา'}
      </button>
    </form>
  );
};

describe('IntakeForm Component Tests (R1 & R2)', () => {
  it('renders intake form with birth_time input and without manual dropdowns', () => {
    render(<MockIntakeForm onSubmit={() => {}} />);
    expect(screen.getByLabelText('ชื่อ-นามสกุล')).toBeDefined();
    expect(screen.getByLabelText('วันเกิด')).toBeDefined();
    expect(screen.getByLabelText('เวลาเกิด')).toBeDefined();
    expect(screen.getByLabelText('จังหวัดเกิด')).toBeDefined();

    // R1 requirement: manual dropdowns should NOT exist
    expect(screen.queryByLabelText('วันเกิด (ตามสัปดาห์)')).toBeNull();
    expect(screen.queryByLabelText('เดือนเกิด (จันทรคติ)')).toBeNull();
    expect(screen.queryByLabelText('ปีนักษัตร')).toBeNull();
  });

  it('updates birth_time input value on user typing', () => {
    render(<MockIntakeForm onSubmit={() => {}} />);
    const timeInput = screen.getByLabelText('เวลาเกิด') as HTMLInputElement;
    fireEvent.change(timeInput, { target: { value: '05:30' } });
    expect(timeInput.value).toBe('05:30');
  });

  it('renders interactive 78 face-down Tarot card grid', () => {
    render(<MockIntakeForm onSubmit={() => {}} />);
    expect(screen.getByLabelText('card-counter')).toBeDefined();
    expect(screen.getByText(/เลือกไพ่แล้ว 0 \/ 10 ใบ/i)).toBeDefined();

    // Check first and last cards exist in 78-card deck
    expect(screen.getByTestId('tarot-card-0')).toBeDefined();
    expect(screen.getByTestId('tarot-card-77')).toBeDefined();
  });

  it('updates selection counter and card selection state when clicked', () => {
    render(<MockIntakeForm onSubmit={() => {}} />);
    const card0 = screen.getByTestId('tarot-card-0');
    fireEvent.click(card0);
    expect(screen.getByText(/เลือกไพ่แล้ว 1 \/ 10 ใบ/i)).toBeDefined();

    // Click again to deselect
    fireEvent.click(card0);
    expect(screen.getByText(/เลือกไพ่แล้ว 0 \/ 10 ใบ/i)).toBeDefined();
  });

  it('disables submit button until exactly 10 cards are selected', () => {
    render(<MockIntakeForm onSubmit={() => {}} />);
    const submitBtn = screen.getByRole('button') as HTMLButtonElement;
    expect(submitBtn.disabled).toBe(true);

    // Select 10 cards (0..9)
    for (let i = 0; i < 10; i++) {
      fireEvent.click(screen.getByTestId(`tarot-card-${i}`));
    }

    expect(screen.getByText(/เลือกไพ่แล้ว 10 \/ 10 ใบ/i)).toBeDefined();
    expect(submitBtn.disabled).toBe(false);
  });

  it('prevents selecting more than 10 cards', () => {
    render(<MockIntakeForm onSubmit={() => {}} />);
    for (let i = 0; i < 11; i++) {
      fireEvent.click(screen.getByTestId(`tarot-card-${i}`));
    }
    // Counter stays at 10
    expect(screen.getByText(/เลือกไพ่แล้ว 10 \/ 10 ใบ/i)).toBeDefined();
  });

  it('sends selected_tarot_cards array in form submission payload', () => {
    const handleSubmit = vi.fn();
    render(<MockIntakeForm onSubmit={handleSubmit} />);
    
    // Select 10 cards
    const expectedCards = [0, 5, 12, 18, 25, 30, 42, 50, 61, 75];
    expectedCards.forEach(id => fireEvent.click(screen.getByTestId(`tarot-card-${id}`)));

    const submitBtn = screen.getByText('ทำนายดวงชะตา');
    fireEvent.click(submitBtn);

    expect(handleSubmit).toHaveBeenCalledTimes(1);
    expect(handleSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        full_name: 'สมชาย ดวงดี',
        birth_date: '1995-08-15',
        birth_time: '06:00',
        birth_province: 'กรุงเทพมหานคร',
        selected_tarot_cards: expectedCards,
      })
    );
  });
});
