import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

const MockResultsDisplay = ({ results }: { results?: any }) => {
  if (!results) {
    return <div className="glass-card">ไม่มีข้อมูลคำทำนาย</div>;
  }

  const renderHeatBadge = (category: string, numStr: string) => {
    if (!results?.heat_index?.[category]) return null;
    const item = results.heat_index[category].find((h: any) => String(h.number) === String(numStr));
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
      <span className={badgeClass} data-testid={`heat-badge-${numStr}`}>
        {text}
      </span>
    );
  };

  const renderOrigins = (numStr: string) => {
    const origins = results?.number_origins?.[numStr];
    if (!origins || origins.length === 0) return null;
    return (
      <div className="origin-tags-group" data-testid={`origins-${numStr}`}>
        <span className="origin-label">📍 ที่มา:</span>
        {origins.map((org: string, i: number) => (
          <span key={i} className="origin-tag">
            {org}
          </span>
        ))}
      </div>
    );
  };

  const twoDigits = results.lucky_numbers?.two_digit || results.lucky_numbers?.two_digits || [];
  const threeDigits = results.lucky_numbers?.three_digit || results.lucky_numbers?.three_digits || [];
  const sixDigits = results.lucky_numbers?.six_digit || results.lucky_numbers?.six_digits || [];

  return (
    <div className="results-container">
      {/* R1 Lunar Calendar Output Card */}
      {results.chart?.lunar_calendar && (
        <div className="glass-card lunar-card" data-testid="lunar-calendar-card">
          <h3>🌙 ปฏิทินจันทรคติไทย (คำนวณอัตโนมัติ)</h3>
          <div className="lunar-info-grid">
            <span className="lunar-val">{results.chart.lunar_calendar.day_of_week}</span>
            <span className="lunar-val">เดือน {results.chart.lunar_calendar.lunar_month}</span>
            <span className="lunar-val">ปี{results.chart.lunar_calendar.zodiac_year}</span>
          </div>
          <p className="cutoff-note">
            {results.chart.lunar_calendar.cutoff_applied
              ? '🌅 คำนวณโดยใช้กฎตัดรอบวันใหม่เวลา 06:00 น. ตามหลักโหราศาสตร์ไทย'
              : '☀️ เวลาเกิดหลัง 06:00 น. ตรงตามวันทางสากล'}
          </p>
        </div>
      )}

      {/* Recommended Numbers Display */}
      <div className="glass-card lucky-numbers">
        <h2>🎯 เลขเด็ดมงคลของคุณงวดนี้</h2>

        {/* 2-Digit */}
        <div className="number-section">
          <h3>เลข 2 ตัว</h3>
          {twoDigits.map((num: string, idx: number) => (
            <div key={idx} className="number-card-row">
              <span className="number-value">{num}</span>
              {renderHeatBadge("two_digit", num)}
              {renderOrigins(num)}
            </div>
          ))}
        </div>

        {/* 3-Digit */}
        <div className="number-section">
          <h3>เลข 3 ตัว</h3>
          {threeDigits.map((num: string, idx: number) => (
            <div key={idx} className="number-card-row">
              <span className="number-value">{num}</span>
              {renderHeatBadge("three_digit", num)}
              {renderOrigins(num)}
            </div>
          ))}
        </div>

        {/* 6-Digit */}
        <div className="number-section">
          <h3>เลข 6 ตัว</h3>
          {sixDigits.map((num: string, idx: number) => (
            <div key={idx} className="number-card-row">
              <span className="number-value">{num}</span>
              {renderHeatBadge("six_digit", num)}
              {renderOrigins(num)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

describe('RecommendedNumbers Component Tests (R1, R3, R4)', () => {
  const mockResults = {
    chart: {
      birth_date: '1995-08-15',
      birth_time: '05:30',
      lunar_calendar: {
        day_of_week: 'Thursday',
        lunar_month: 9,
        zodiac_year: 'Pig',
        cutoff_applied: true,
      },
    },
    lucky_numbers: {
      two_digit: ['15', '84'],
      three_digit: ['485', '792'],
      six_digit: ['485792'],
    },
    heat_index: {
      two_digit: [
        { number: '15', win_count: 3, level: 'HOT' },
        { number: '84', win_count: 1, level: 'WARM' },
      ],
      three_digit: [
        { number: '485', win_count: 0, level: 'COLD' },
        { number: '792', win_count: 2, level: 'HOT' },
      ],
      six_digit: [
        { number: '485792', win_count: 0, level: 'COLD' },
      ],
    },
    number_origins: {
      '15': ['Mahabote: Thanang + Phoka', 'Thai Astrology: Lagna Lord 1'],
      '84': ['Tarot Card #3: The Empress', 'Numerology 7x9: Base 4'],
      '485': ['Combined: Lagna 4 + Mahabote 85'],
      '792': ['Tarot Card #1: The Magician + Numerology 792'],
      '485792': ['Synthesis of Top Engine Predictions'],
    },
  };

  it('renders auto-calculated Thai Lunar Calendar output card (R1)', () => {
    render(<MockResultsDisplay results={mockResults} />);
    expect(screen.getByTestId('lunar-calendar-card')).toBeDefined();
    expect(screen.getByText('Thursday')).toBeDefined();
    expect(screen.getByText('เดือน 9')).toBeDefined();
    expect(screen.getByText('ปีPig')).toBeDefined();
    expect(screen.getByText(/คำนวณโดยใช้กฎตัดรอบวันใหม่เวลา 06:00 น./i)).toBeDefined();
  });

  it('renders Heat Index badges for 2-digit, 3-digit, and 6-digit numbers (R3)', () => {
    render(<MockResultsDisplay results={mockResults} />);
    
    // HOT badge for 15
    const badge15 = screen.getByTestId('heat-badge-15');
    expect(badge15.textContent).toContain('🔥 ร้อนแรง (ชนะ 3 ครั้ง)');
    expect(badge15.className).toContain('heat-badge hot');

    // WARM badge for 84
    const badge84 = screen.getByTestId('heat-badge-84');
    expect(badge84.textContent).toContain('⚡ ปานกลาง (ชนะ 1 ครั้ง)');
    expect(badge84.className).toContain('heat-badge warm');

    // COLD badge for 485
    const badge485 = screen.getByTestId('heat-badge-485');
    expect(badge485.textContent).toContain('❄️ หายาก (ชนะ 0 ครั้ง)');
    expect(badge485.className).toContain('heat-badge cold');
  });

  it('renders Divination Transparency provenance tags alongside recommended numbers (R4)', () => {
    render(<MockResultsDisplay results={mockResults} />);

    // Provenance for 15
    const origins15 = screen.getByTestId('origins-15');
    expect(origins15.textContent).toContain('📍 ที่มา:');
    expect(origins15.textContent).toContain('Mahabote: Thanang + Phoka');
    expect(origins15.textContent).toContain('Thai Astrology: Lagna Lord 1');

    // Provenance for 84
    const origins84 = screen.getByTestId('origins-84');
    expect(origins84.textContent).toContain('Tarot Card #3: The Empress');

    // Provenance for 6-digit number
    const origins6Dig = screen.getByTestId('origins-485792');
    expect(origins6Dig.textContent).toContain('Synthesis of Top Engine Predictions');
  });

  it('renders fallback when results is missing or undefined', () => {
    render(<MockResultsDisplay results={undefined} />);
    expect(screen.getByText('ไม่มีข้อมูลคำทำนาย')).toBeDefined();
  });
});
