from metropiness import Metropiness

m = Metropiness()

def test_nyc():
    result = m.classify(40.7128, -74.0060)
    assert result[0] == 1
    assert 'Metropolitan core' in result[1]

def test_providence():
    result = m.classify(41.8240, -71.4128)
    assert result[0] == 1
    assert 'Metropolitan core' in result[1]

def test_ocean_returns_none():
    result = m.classify(0, 0)  # middle of the ocean
    assert result is None

def test_somewhere_Alaska():
    result = m.classify(58.36739751736477, -156.63991439185367)
    assert result[0] == 10
    assert 'Rural area' in result[1]

def test_PuertoRico_mismatch():
    local = m.get_tract(18.191945420614736, -66.33825887046254)
    api = m.census_api_lookup(18.191945420614736, -66.33825887046254)
    local_ruca = m.get_ruca(local)
    api_ruca = m.get_ruca(api)
    assert int(local_ruca["PrimaryRUCA"]) == int(api_ruca["PrimaryRUCA"])
