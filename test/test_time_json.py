def test_incl_time_module_execution(run_stkt):
    code = """
    incl "time" as t

    let t1: i64 = t.now_ms()
    t.sleep_ms(20)
    let t2: i64 = t.now_ms()
    let elapsed: i64 = t.elapsed_ms(t1)
    let threshold: i64 = (i64)15
    let ok: bool = elapsed >= threshold
    onscreen "Time OK: {ok}"
    """
    output = run_stkt(code)
    assert "Time OK: true" in output


def test_incl_json_module_execution(run_stkt):
    code = """
    incl "json" as j

    let s_name: str = j.stringify_str("Bob")
    let s_age: str = j.stringify_i32(42)
    let s_ok: str = j.stringify_bool(false)

    let kv1: str = j.stringify_kv("username", s_name)
    let kv2: str = j.stringify_kv("score", s_age)
    let kv3: str = j.stringify_kv("admin", s_ok)

    let doc: str = "{" + kv1 + ", " + kv2 + ", " + kv3 + "}"

    let has_user: bool = j.has_key(doc, "username")
    let parsed_user: str = j.get_str(doc, "username")
    let parsed_score: i32 = j.get_int(doc, "score")
    let parsed_admin: bool = j.get_bool(doc, "admin")

    onscreen "User: {parsed_user}, Score: {parsed_score}, Admin: {parsed_admin}"
    """
    output = run_stkt(code)
    assert "User: Bob, Score: 42, Admin: false" in output


def test_incl_json_dump_and_parse_whole_object(run_stkt):
    code = """
    incl "json" as j

    let payload: hmap[str: str] = {}
    payload.set("app", "stkt-service")
    payload.set("host", "127.0.0.1")
    payload.set("port", "8080")

    let serialized: str = j.dump_object(payload)

    let parsed: hmap[str: str] = j.parse_object(serialized)
    let app_val: str = parsed.get("app")
    let host_val: str = parsed.get("host")
    let port_val: str = parsed.get("port")

    onscreen "App: {app_val}, Host: {host_val}:{port_val}"
    """
    output = run_stkt(code)
    assert "App: stkt-service, Host: 127.0.0.1:8080" in output


def test_incl_json_complex_nested_and_file_io(run_stkt, tmp_path):
    json_file = tmp_path / "server_config.json"
    json_file.write_text("""{
  "service": "auth-hub",
  "version": "2.4.1",
  "port": 9000,
  "debug": false,
  "rate_limit": 1500,
  "ssl_enabled": true,
  "cluster": {
    "region": "us-east-1",
    "replicas": 5
  }
}""")

    filepath = str(json_file)
    code = """
    incl "io" as io
    incl "json" as j

    let content: str = io.read_text("__FILE_PATH__")

    let svc: str = j.get_str(content, "service")
    let ver: str = j.get_str(content, "version")
    let port: i32 = j.get_int(content, "port")
    let debug: bool = j.get_bool(content, "debug")
    let rate: i32 = j.get_int(content, "rate_limit")
    let ssl: bool = j.get_bool(content, "ssl_enabled")

    // Nested extraction
    let region: str = j.get_str(content, "region")
    let replicas: i32 = j.get_int(content, "replicas")

    // Key existence checks
    let has_ssl: bool = j.has_key(content, "ssl_enabled")
    let has_missing: bool = j.has_key(content, "database_url")

    // Fallbacks via .or()
    let timeout: i32 = j.get_int(content, "timeout").or(30)
    let db_host: str = j.get_str(content, "database_host").or("localhost")

    // Whole object dictionary parsing
    let config_map: hmap[str: str] = j.parse_object(content)
    let map_svc: str = config_map.get("service")
    let map_port: str = config_map.get("port")

    onscreen "Svc: {svc} v{ver}, Port: {port}, Debug: {debug}"
    onscreen "Rate: {rate}, SSL: {ssl}, Region: {region}, Replicas: {replicas}"
    onscreen "Has SSL: {has_ssl}, Missing: {has_missing}"
    onscreen "Timeout: {timeout}, DB: {db_host}"
    onscreen "Map Svc: {map_svc}, Map Port: {map_port}"
    """.replace("__FILE_PATH__", filepath)

    output = run_stkt(code)
    assert "Svc: auth-hub v2.4.1, Port: 9000, Debug: false" in output
    assert "Rate: 1500, SSL: true, Region: us-east-1, Replicas: 5" in output
    assert "Has SSL: true, Missing: false" in output
    assert "Timeout: 30, DB: localhost" in output
    assert "Map Svc: auth-hub, Map Port: 9000" in output
