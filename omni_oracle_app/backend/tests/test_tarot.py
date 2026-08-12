import pytest
from app.engines.tarot import TarotEngine

def test_draw_celtic_cross():
    engine = TarotEngine()
    spread = engine.draw_celtic_cross()
    
    assert len(spread) == 10
    
    # Check that all cards are unique
    card_ids = [card['id'] for card in spread]
    assert len(set(card_ids)) == 10
    
    # Check structure of a card
    for card in spread:
        assert 'id' in card
        assert 'name' in card
        assert 'type' in card # Major or Minor Arcana
        assert 'is_reversed' in card
        assert 'meaning' in card
        assert 'position_meaning' in card

def test_card_database_integrity():
    engine = TarotEngine()
    assert len(engine.deck) == 78
    
    major_arcana = [c for c in engine.deck if c['type'] == 'Major Arcana']
    assert len(major_arcana) == 22
    
    minor_arcana = [c for c in engine.deck if c['type'] == 'Minor Arcana']
    assert len(minor_arcana) == 56
