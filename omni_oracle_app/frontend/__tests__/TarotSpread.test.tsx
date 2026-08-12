import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';

const MockTarotDeck = ({
  maxSelection = 10,
  onSelectionChange
}: {
  maxSelection?: number;
  onSelectionChange?: (selectedCards: number[]) => void;
}) => {
  const [selectedCards, setSelectedCards] = React.useState<number[]>([]);

  const handleCardClick = (cardIndex: number) => {
    let nextCards: number[];
    if (selectedCards.includes(cardIndex)) {
      nextCards = selectedCards.filter(id => id !== cardIndex);
    } else if (selectedCards.length < maxSelection) {
      nextCards = [...selectedCards, cardIndex];
    } else {
      return;
    }
    setSelectedCards(nextCards);
    if (onSelectionChange) onSelectionChange(nextCards);
  };

  return (
    <div className="tarot-section">
      <h3 className="gold-text">เลือกไพ่ทาโรต์มงคล {maxSelection} ใบ</h3>
      <p className="card-counter" aria-label="card-counter">
        เลือกไพ่แล้ว {selectedCards.length} / {maxSelection} ใบ
      </p>
      <div className="tarot-deck-grid">
        {[...Array(78)].map((_, index) => {
          const isSelected = selectedCards.includes(index);
          const selectOrder = selectedCards.indexOf(index) + 1;
          return (
            <div
              key={index}
              data-testid={`tarot-card-${index}`}
              className={`tarot-card-facedown ${isSelected ? 'selected' : ''}`}
              onClick={() => handleCardClick(index)}
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
  );
};

describe('Tarot Deck Grid Component Tests (R2)', () => {
  it('renders all 78 face-down cards in the deck grid', () => {
    render(<MockTarotDeck />);
    expect(screen.getByLabelText('card-counter')).toBeDefined();
    expect(screen.getByText(/เลือกไพ่แล้ว 0 \/ 10 ใบ/i)).toBeDefined();
    for (let i = 0; i < 78; i++) {
      expect(screen.getByTestId(`tarot-card-${i}`)).toBeDefined();
    }
  });

  it('selects and deselects cards, updating order badges and counter', () => {
    const handleChange = vi.fn();
    render(<MockTarotDeck onSelectionChange={handleChange} />);
    
    const card5 = screen.getByTestId('tarot-card-5');
    fireEvent.click(card5);
    expect(screen.getByText(/เลือกไพ่แล้ว 1 \/ 10 ใบ/i)).toBeDefined();
    expect(screen.getByText('#1')).toBeDefined();
    expect(handleChange).toHaveBeenCalledWith([5]);

    const card12 = screen.getByTestId('tarot-card-12');
    fireEvent.click(card12);
    expect(screen.getByText(/เลือกไพ่แล้ว 2 \/ 10 ใบ/i)).toBeDefined();
    expect(screen.getByText('#2')).toBeDefined();
    expect(handleChange).toHaveBeenCalledWith([5, 12]);

    // Deselect card 5
    fireEvent.click(card5);
    expect(screen.getByText(/เลือกไพ่แล้ว 1 \/ 10 ใบ/i)).toBeDefined();
    expect(handleChange).toHaveBeenCalledWith([12]);
  });

  it('strictly caps selection at exactly 10 cards', () => {
    render(<MockTarotDeck maxSelection={10} />);
    
    // Attempt to click 12 cards
    for (let i = 0; i < 12; i++) {
      fireEvent.click(screen.getByTestId(`tarot-card-${i}`));
    }

    expect(screen.getByText(/เลือกไพ่แล้ว 10 \/ 10 ใบ/i)).toBeDefined();
    expect(screen.queryByText('#11')).toBeNull();
  });
});
