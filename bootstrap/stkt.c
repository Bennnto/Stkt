#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <stdarg.h>
#include <ctype.h>
#include <sys/time.h>
#include <unistd.h>
static int __attribute__((unused)) __stkt_argc = 0;
static char** __attribute__((unused)) __stkt_argv = NULL;
static inline __attribute__((unused)) void stkt_exit(int32_t code) { exit(code); }
static inline __attribute__((unused)) int32_t stkt_scan_i32() { int32_t v=0; if (scanf("%d", &v) != 1) return 0; return v; }
static inline __attribute__((unused)) double stkt_scan_f64() { double v=0; if (scanf("%lf", &v) != 1) return 0; return v; }
static inline __attribute__((unused)) char* stkt_scan_str() { char* b = (char*)malloc(1024); if (!b) return ""; if (!fgets(b, 1024, stdin)) { b[0] = 0; return b; } size_t l = strlen(b); if (l > 0 && b[l-1] == '\n') b[l-1] = 0; if (l > 1 && b[l-2] == '\r') b[l-2] = 0; return b; }
static inline __attribute__((unused)) bool stkt_scan_bool() { char b[16]; if (scanf("%15s", b) != 1) return false; return (strcmp(b, "true") == 0 || strcmp(b, "1") == 0); }
static inline __attribute__((unused)) char stkt_scan_char() { char c = 0; if (scanf(" %c", &c) != 1) return 0; return c; }
typedef struct __stkt_arena_chunk { char* memory; size_t capacity; size_t offset; struct __stkt_arena_chunk* next; } __stkt_arena_chunk;
typedef struct { __stkt_arena_chunk* current; size_t default_chunk_size; } __stkt_arena;
static inline __attribute__((unused)) int64_t stkt_arena_create(int32_t chunk_size) { if (chunk_size <= 0) chunk_size = 65536; __stkt_arena* a = (__stkt_arena*)malloc(sizeof(__stkt_arena)); a->default_chunk_size = (size_t)chunk_size; __stkt_arena_chunk* c = (__stkt_arena_chunk*)malloc(sizeof(__stkt_arena_chunk)); c->memory = (char*)malloc((size_t)chunk_size); c->capacity = (size_t)chunk_size; c->offset = 0; c->next = NULL; a->current = c; return (int64_t)(uintptr_t)a; }
static inline __attribute__((unused)) void* stkt_arena_alloc(__stkt_arena* a, size_t size) { if (!a) return NULL; size = (size + 7) & ~7; __stkt_arena_chunk* c = a->current; if (c->offset + size > c->capacity) { size_t new_cap = a->default_chunk_size; if (size > new_cap) new_cap = size; __stkt_arena_chunk* nc = (__stkt_arena_chunk*)malloc(sizeof(__stkt_arena_chunk)); nc->memory = (char*)malloc(new_cap); nc->capacity = new_cap; nc->offset = 0; nc->next = c; a->current = nc; c = nc; } void* ptr = (void*)(c->memory + c->offset); c->offset += size; return ptr; }
static inline __attribute__((unused)) char* stkt_arena_alloc_str(int64_t handle, const char* s) { __stkt_arena* a = (__stkt_arena*)(uintptr_t)handle; if (!a || !s) return ""; size_t len = strlen(s); char* dest = (char*)stkt_arena_alloc(a, len + 1); if (!dest) return ""; memcpy(dest, s, len); dest[len] = 0; return dest; }
static inline __attribute__((unused)) void stkt_arena_reset(int64_t handle) { __stkt_arena* a = (__stkt_arena*)(uintptr_t)handle; if (!a) return; __stkt_arena_chunk* c = a->current; while (c) { c->offset = 0; c = c->next; } }
static inline __attribute__((unused)) void stkt_arena_destroy(int64_t handle) { __stkt_arena* a = (__stkt_arena*)(uintptr_t)handle; if (!a) return; __stkt_arena_chunk* c = a->current; while (c) { __stkt_arena_chunk* next = c->next; if (c->memory) free(c->memory); free(c); c = next; } free(a); }
static inline __attribute__((unused)) char* stkt_format(const char* fmt, ...) { va_list args, args2; va_start(args, fmt); va_copy(args2, args); int len = vsnprintf(NULL, 0, fmt, args); va_end(args); if (len < 0) { va_end(args2); return ""; } char* b = (char*)malloc((size_t)len + 1); if (!b) { va_end(args2); return ""; } vsnprintf(b, (size_t)len + 1, fmt, args2); va_end(args2); return b; }
static bool __attribute__((unused)) __stkt_has_error = false;
static inline __attribute__((unused)) void __stkt_set_err() { __stkt_has_error = true; }
static inline __attribute__((unused)) void __stkt_clear_err() { __stkt_has_error = false; }

#define STKT_SLICE_DEFINE(TYPE, NAME) typedef struct { TYPE* data; size_t len; size_t cap; } __stkt_slice_buf_##NAME; typedef struct { __stkt_slice_buf_##NAME* buf; } NAME;
STKT_SLICE_DEFINE(int32_t, stkt_slice_i32)
STKT_SLICE_DEFINE(int64_t, stkt_slice_i64)
STKT_SLICE_DEFINE(float, stkt_slice_f32)
STKT_SLICE_DEFINE(double, stkt_slice_f64)
STKT_SLICE_DEFINE(char*, stkt_slice_str)
#define STKT_SLICE_INIT(s) do { (s).buf = malloc(sizeof(*((s).buf))); (s).buf->data = NULL; (s).buf->len = 0; (s).buf->cap = 0; } while(0)
#define STKT_SLICE_APPEND(s, val) do { if ((s).buf->len >= (s).buf->cap) { (s).buf->cap = ((s).buf->cap == 0) ? 4 : ((s).buf->cap * 2); (s).buf->data = realloc((s).buf->data, (s).buf->cap * sizeof(*((s).buf->data))); } (s).buf->data[(s).buf->len++] = (val); } while(0)
#define STKT_SLICE_POP(s) ((s).buf->data[--((s).buf->len)])
#define STKT_SLICE_LEN(s) ((int32_t)((s).buf->len))

static inline __attribute__((unused)) char* stkt_str_concat(const char* s1, const char* s2) { if (!s1) s1 = ""; if (!s2) s2 = ""; size_t l1 = strlen(s1); size_t l2 = strlen(s2); char* r = (char*)malloc(l1 + l2 + 1); if (!r) return ""; memcpy(r, s1, l1); memcpy(r + l1, s2, l2); r[l1 + l2] = 0; return r; }
static inline __attribute__((unused)) char* stkt_str_slice(const char* s, int32_t start, int32_t end) { if (!s) return ""; int32_t l = (int32_t)strlen(s); if (start < 0) start = 0; if (end > l) end = l; if (start >= end) { char* e = (char*)malloc(1); e[0] = 0; return e; } int32_t sub_len = end - start; char* r = (char*)malloc(sub_len + 1); if (!r) return ""; memcpy(r, s + start, sub_len); r[sub_len] = 0; return r; }
static inline __attribute__((unused)) stkt_slice_str stkt_str_split(const char* s, const char* sep) { stkt_slice_str res; STKT_SLICE_INIT(res); if (!s || !sep) return res; size_t sl = strlen(sep); if (sl == 0) { STKT_SLICE_APPEND(res, strdup(s)); return res; } const char* curr = s; const char* found; while ((found = strstr(curr, sep)) != NULL) { size_t pl = found - curr; char* p = (char*)malloc(pl + 1); memcpy(p, curr, pl); p[pl] = 0; STKT_SLICE_APPEND(res, p); curr = found + sl; } STKT_SLICE_APPEND(res, strdup(curr)); return res; }
static inline __attribute__((unused)) char* stkt_str_trim(const char* s) { if (!s) return ""; while (isspace((unsigned char)*s)) s++; if (*s == 0) return strdup(""); const char* end = s + strlen(s) - 1; while (end > s && isspace((unsigned char)*end)) end--; size_t l = end - s + 1; char* r = (char*)malloc(l + 1); memcpy(r, s, l); r[l] = 0; return r; }
static inline __attribute__((unused)) bool stkt_str_contains(const char* s, const char* sub) { if (!s || !sub) return false; return strstr(s, sub) != NULL; }

typedef struct __stkt_map_entry_str_i32 { char* key; int32_t val; struct __stkt_map_entry_str_i32* next; } __stkt_map_entry_str_i32;
typedef struct { __stkt_map_entry_str_i32* buckets[64]; int32_t size; } __stkt_map_str_i32;
static inline __attribute__((unused)) uint32_t __stkt_hash_str(const char* s) { uint32_t h = 2166136261u; if (!s) return 0; while (*s) { h ^= (uint8_t)*s++; h *= 16777619u; } return h; }
static inline __attribute__((unused)) __stkt_map_str_i32* __stkt_map_create_str_i32() { return (__stkt_map_str_i32*)calloc(1, sizeof(__stkt_map_str_i32)); }
static inline __attribute__((unused)) void __stkt_map_set_str_i32(__stkt_map_str_i32* m, const char* key, int32_t val) { if (!m || !key) return; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { curr->val = val; return; } curr = curr->next; } __stkt_map_entry_str_i32* entry = (__stkt_map_entry_str_i32*)malloc(sizeof(__stkt_map_entry_str_i32)); entry->key = strdup(key); entry->val = val; entry->next = m->buckets[idx]; m->buckets[idx] = entry; m->size++; }
static inline __attribute__((unused)) int32_t __stkt_map_get_str_i32(__stkt_map_str_i32* m, const char* key) { if (!m || !key) { __stkt_set_err(); return 0; } uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { return curr->val; } curr = curr->next; } __stkt_set_err(); return 0; }
static inline __attribute__((unused)) bool __stkt_map_has_str_i32(__stkt_map_str_i32* m, const char* key) { if (!m || !key) return false; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) return true; curr = curr->next; } return false; }
static inline __attribute__((unused)) stkt_slice_str __stkt_map_keys_str_i32(__stkt_map_str_i32* m) { stkt_slice_str res; STKT_SLICE_INIT(res); if (!m) return res; for (int i = 0; i < 64; i++) { __stkt_map_entry_str_i32* curr = m->buckets[i]; while (curr) { STKT_SLICE_APPEND(res, curr->key); curr = curr->next; } } return res; }
typedef struct __stkt_map_entry_str_str { char* key; char* val; struct __stkt_map_entry_str_str* next; } __stkt_map_entry_str_str;
typedef struct { __stkt_map_entry_str_str* buckets[64]; int32_t size; } __stkt_map_str_str;
static inline __attribute__((unused)) __stkt_map_str_str* __stkt_map_create_str_str() { return (__stkt_map_str_str*)calloc(1, sizeof(__stkt_map_str_str)); }
static inline __attribute__((unused)) void __stkt_map_set_str_str(__stkt_map_str_str* m, const char* key, const char* val) { if (!m || !key) return; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_str* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { if (curr->val) free(curr->val); curr->val = val ? strdup(val) : strdup(""); return; } curr = curr->next; } __stkt_map_entry_str_str* entry = (__stkt_map_entry_str_str*)malloc(sizeof(__stkt_map_entry_str_str)); entry->key = strdup(key); entry->val = val ? strdup(val) : strdup(""); entry->next = m->buckets[idx]; m->buckets[idx] = entry; m->size++; }
static inline __attribute__((unused)) char* __stkt_map_get_str_str(__stkt_map_str_str* m, const char* key) { if (!m || !key) { __stkt_set_err(); return ""; } uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_str* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { return curr->val; } curr = curr->next; } __stkt_set_err(); return ""; }
static inline __attribute__((unused)) bool __stkt_map_has_str_str(__stkt_map_str_str* m, const char* key) { if (!m || !key) return false; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_str* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) return true; curr = curr->next; } return false; }
static inline __attribute__((unused)) stkt_slice_str __stkt_map_keys_str_str(__stkt_map_str_str* m) { stkt_slice_str res; STKT_SLICE_INIT(res); if (!m) return res; for (int i = 0; i < 64; i++) { __stkt_map_entry_str_str* curr = m->buckets[i]; while (curr) { STKT_SLICE_APPEND(res, curr->key); curr = curr->next; } } return res; }

static inline __attribute__((unused)) bool stkt_file_exists(const char* path) { if (!path) return false; FILE* f = fopen(path, "r"); if (f) { fclose(f); return true; } return false; }
static inline __attribute__((unused)) bool stkt_file_write(const char* path, const char* content) { if (!path) return false; FILE* f = fopen(path, "w"); if (!f) return false; fputs(content ? content : "", f); fclose(f); return true; }
static inline __attribute__((unused)) bool stkt_file_append(const char* path, const char* content) { if (!path) return false; FILE* f = fopen(path, "a"); if (!f) return false; fputs(content ? content : "", f); fclose(f); return true; }
static inline __attribute__((unused)) int32_t stkt_file_size(const char* path) { if (!path) return -1; FILE* f = fopen(path, "rb"); if (!f) return -1; fseek(f, 0, SEEK_END); long s = ftell(f); fclose(f); return (int32_t)s; }
static inline __attribute__((unused)) char* stkt_file_read(const char* path) { if (!path) return ""; FILE* f = fopen(path, "rb"); if (!f) return ""; fseek(f, 0, SEEK_END); long s = ftell(f); fseek(f, 0, SEEK_SET); char* b = (char*)malloc(s + 1); if (!b) { fclose(f); return ""; } size_t r = fread(b, 1, s, f); b[r] = 0; fclose(f); return b; }

static inline __attribute__((unused)) int32_t stkt_args_count() { return (int32_t)__stkt_argc; }
static inline __attribute__((unused)) stkt_slice_str stkt_get_args() { stkt_slice_str args; STKT_SLICE_INIT(args); for (int i = 0; i < __stkt_argc; i++) { STKT_SLICE_APPEND(args, __stkt_argv[i]); } return args; }
static inline __attribute__((unused)) char* stkt_get_env(const char* key) { if (!key) return ""; char* v = getenv(key); return v ? v : (char*)""; }
static inline __attribute__((unused)) int32_t stkt_system(const char* cmd) { if (!cmd) return -1; return system(cmd); }

static inline __attribute__((unused)) int64_t stkt_time_now_ms() { struct timeval tv; gettimeofday(&tv, NULL); return ((int64_t)tv.tv_sec * 1000) + (tv.tv_usec / 1000); }
static inline __attribute__((unused)) int64_t stkt_time_now_us() { struct timeval tv; gettimeofday(&tv, NULL); return ((int64_t)tv.tv_sec * 1000000) + tv.tv_usec; }
static inline __attribute__((unused)) void stkt_time_sleep_ms(int32_t ms) { if (ms > 0) usleep((useconds_t)ms * 1000); }

typedef enum {
    TokenKind_TokEof,
    TokenKind_TokInt,
    TokenKind_TokStr,
    TokenKind_TokIdent,
    TokenKind_TokAssign,
    TokenKind_TokPlus,
    TokenKind_TokMinus,
    TokenKind_TokStar,
    TokenKind_TokSlash,
    TokenKind_TokLParen,
    TokenKind_TokRParen,
    TokenKind_TokLBrace,
    TokenKind_TokRBrace,
    TokenKind_TokLBracket,
    TokenKind_TokRBracket,
    TokenKind_TokLet,
    TokenKind_TokProc,
    TokenKind_TokIf,
    TokenKind_TokElse,
    TokenKind_TokWhile,
    TokenKind_TokReturn,
    TokenKind_TokOnscreen,
    TokenKind_TokOnkey,
    TokenKind_TokColon,
    TokenKind_TokComma,
    TokenKind_TokSemicolon,
    TokenKind_TokEq,
    TokenKind_TokNe,
    TokenKind_TokLt,
    TokenKind_TokGt,
    TokenKind_TokLe,
    TokenKind_TokGe,
    TokenKind_TokAnd,
    TokenKind_TokOr,
    TokenKind_TokNot,
    TokenKind_TokBreak,
    TokenKind_TokContinue,
    TokenKind_TokConst,
    TokenKind_TokFor,
    TokenKind_TokLoop,
    TokenKind_TokStep,
    TokenKind_TokIn,
    TokenKind_TokMatch,
    TokenKind_TokCase,
    TokenKind_TokDefault,
    TokenKind_TokQuestion,
    TokenKind_TokLambda,
    TokenKind_TokTrue,
    TokenKind_TokFalse,
    TokenKind_TokFloat,
    TokenKind_TokChar,
    TokenKind_TokType,
    TokenKind_TokDot,
    TokenKind_TokEnum,
    TokenKind_TokPop,
    TokenKind_TokAppend,
    TokenKind_TokLen,
    TokenKind_TokHMap,
    TokenKind_TokIsok,
    TokenKind_TokSync,
    TokenKind_TokExport,
    TokenKind_TokAs,
} TokenKind;

typedef struct {
       TokenKind kind;
       int32_t val;
       float fval;
       char* text;
       int32_t next_pos;
       int32_t line;
} Token;

typedef struct {
       char* name;
       char* type_name;
       char* val;
       int32_t next;
} LetNode;
typedef struct {
       char* name;
       char* val;
       int32_t next;
} AssignNode;
typedef struct {
       char* cond;
       char* body;
       int32_t next;
} WhileNode;
typedef struct {
       char* cond;
       char* body;
       char* else_body;
       int32_t next;
} IfNode;
typedef struct {
       char* val;
       char* type_name;
       int32_t next;
} PrintNode;
typedef struct {
       char* val;
       int32_t next;
} ReturnNode;
typedef struct {
       char* name;
       char* ret_type;
       char* params;
       char* body;
       int32_t next;
} ProcNode;
typedef struct {
       char* name;
       char* args;
       int32_t next;
} CallNode;
typedef struct {
       char* name;
       char* size;
       char* type_name;
       char* element;
       int32_t next;
} ArrayDeclNode;
typedef struct {
       char* name;
       char* index;
       char* val;
       int32_t next;
} IndexAssignNode;
typedef struct {
       char* name;
       char* index;
       int32_t next;
} IndexAccessNode;
typedef struct {
       char* target_type;
       char* val;
       int32_t next;
} CastNode;
typedef struct {
       int32_t next;
} BreakNode;
typedef struct {
       int32_t next;
} ContinueNode;
typedef struct {
       char* name;
       char* type_name;
       char* val;
       int32_t next;
} ConstNode;
typedef struct {
       char* type_name;
       int32_t next;
} ScanNode;
typedef struct {
       char* fmt_str;
       char* arg_str;
       int32_t next;
} InterpolatedStrNode;
typedef struct {
       char* init;
       char* cond;
       char* iter;
       char* body;
       int32_t next;
} ForNode;
typedef struct {
       char* times;
       char* step_val;
       char* body;
       int32_t next;
} LoopNode;
typedef struct {
       char* ident;
       char* collection;
       char* body;
       int32_t next;
} ForinNode;
typedef struct {
       char* target;
       char* body;
       bool is_default;
       int32_t next;
} CaseNode;
typedef struct {
       char* cond;
       char* cases_code;
       int32_t next;
} MatchNode;
typedef struct {
       char* cond;
       char* true_block;
       char* false_block;
       int32_t next;
} TernaryNode;
typedef struct {
       char* operand;
       char* ops;
       int32_t next;
} UnaryNode;
typedef struct {
       char* id;
       char* ret_type;
       char* params;
       char* body;
       int32_t next;
} LambdaNode;
typedef struct {
       char* ident;
       char* fields;
       int32_t next;
} TypeDeclNode;
typedef struct {
       char* ident;
       char* type_name;
       int32_t next;
} FieldNode;
typedef struct {
       char* target;
       char* fields;
       int32_t next;
} TypeAccessNode;
typedef struct {
       char* ident;
       char* variants;
       int32_t next;
} EnumNode;
typedef struct {
       char* ident;
       char* variant;
       int32_t next;
} EnumAccessNode;
typedef struct {
       char* code;
       int32_t next_pos;
} StmtResult;
typedef struct {
       char* name;
       char* elem_type;
       char* elements;
       int32_t next;
} SliceDeclNode;
typedef struct {
       char* arr;
       char* val;
       int32_t next;
} AppendNode;
typedef struct {
       char* arr;
       int32_t next;
} PopNode;
typedef struct {
       char* expr;
       char* msg;
       char* type_name;
       int32_t next;
} IsOkNode;
typedef struct {
       char* module_path;
       char* alias;
       int32_t next;
} SyncNode;
typedef struct {
       char* expr;
       char* fallback;
       char* type_name;
       int32_t next;
} OrNode;
typedef struct {
       bool needs_slices;
       bool needs_strings;
       bool needs_hmap;
       bool needs_io;
       bool needs_os;
       bool needs_error;
       bool needs_time;
} RuntimeFeatures;
typedef struct {
       char* types;
       char* decls;
       char* procs;
} ProgramParts;






typedef struct {
       char* text;
       int32_t next_pos;
} ParseResult;




char* get_runtime_headers();
char* get_runtime_core();
char* get_runtime_slices();
char* get_runtime_error();
char* get_runtime_strings();
char* get_runtime_io();
char* get_runtime_hmap();
char* get_runtime_os();
char* get_runtime_time();
char* get_full_runtime();

bool is_digit(char c);
bool is_alpha(char c);
bool is_primitive_type(char* word);
int32_t skip_whitespace(char* src, int32_t start);
TokenKind check_keyword(char* word);
Token next_token(char* src, int32_t start);

char* to_c_type(char* stkt_t);
RuntimeFeatures detect_features(char* code);
char* gen_let(LetNode node);
char* gen_assign(AssignNode node);
char* gen_if(IfNode node);
char* gen_while(WhileNode node);
char* gen_print(PrintNode node);
char* gen_return(ReturnNode node);
char* gen_proc(ProcNode node);
char* gen_break(BreakNode node);
char* gen_continue(ContinueNode node);
char* gen_const(ConstNode node);
char* gen_call(CallNode node);
char* gen_array_decl(ArrayDeclNode node);
char* gen_index_assign(IndexAssignNode node);
char* gen_index_access(IndexAccessNode node);
char* gen_cast(CastNode node);
char* gen_interpolate(InterpolatedStrNode node);
char* gen_for(ForNode node);
char* gen_loop(LoopNode node);
char* gen_for_in(ForinNode node);
char* gen_ternary(TernaryNode node);
char* gen_unary(UnaryNode node);
char* gen_lambda(LambdaNode node);
char* gen_case(CaseNode node);
char* gen_match(MatchNode node);
char* gen_field(FieldNode node);
bool is_struct_name(char* src, char* name);
bool is_enum_name(char* src, char* name);
bool is_module_name(char* src, char* name);
char* gen_typeaccess(char* src, TypeAccessNode node);
char* gen_enum(EnumNode node);
char* gen_enumaccess(EnumAccessNode node);
char* gen_typedecl(TypeDeclNode node);
char* gen_scan(ScanNode node);
bool is_slice_var(char* src, char* name);
bool is_hmap_var(char* src, char* name);
bool is_hmap_str_str(char* src, char* name);
char* to_slice_c_type(char* elem_t);
char* gen_slice_decl(SliceDeclNode node);
char* gen_append(AppendNode node);
char* gen_index_assign_slice(char* src, IndexAssignNode node);
char* gen_isok(IsOkNode node);
char* gen_or(OrNode node);
char* gen_headers();
char* gen_runtime(RuntimeFeatures features);
char* gen_aliased_proc(ProcNode node, char* alias);
char* gen_program(char* procs, char* main_body);

bool file_exists(char* path);
bool write_text(char* path, char* content);
char* read_text(char* path);
bool append_text(char* path, char* content);
int32_t file_size(char* path);

int32_t arg_count();
stkt_slice_str get_args();
char* get_env(char* key);
int32_t system_cmd(char* cmd);

bool is_already_sync(stkt_slice_str synced, char* file);
char* clean_module_path(char* raw);
char* find_var_type(char* src, char* name);
SyncNode parse_sync(char* src, int32_t start);
ParseResult parse_grouped_expr(char* src, int32_t start);
bool is_valid_interp_var(char* var_expr);
ParseResult parse_interpolated_str(char* s_val, int32_t next_p);
ParseResult parse_idx_atom(char* src, int32_t start);
ParseResult parse_idx_expr(char* src, int32_t start);
ParseResult parse_primary(char* src, int32_t start);
ParseResult parse_term(char* src, int32_t start);
bool is_str_operand(char* src, char* expr);
ParseResult parse_additive(char* src, int32_t start);
ParseResult parse_relational(char* src, int32_t start);
ParseResult parse_equality(char* src, int32_t start);
ParseResult parse_logical_and(char* src, int32_t start);
ParseResult parse_expr(char* src, int32_t start);
ParseResult parse_ternary(char* src, int32_t start);
LetNode parse_let(char* src, int32_t start);
ArrayDeclNode parse_array_decl(char* src, int32_t start);
AssignNode parse_assign(char* src, int32_t start);
IndexAssignNode parse_index_assign(char* src, int32_t start);
CallNode parse_call(char* src, int32_t start);
PrintNode parse_onscreen(char* src, int32_t start);
ReturnNode parse_return(char* src, int32_t start);
BreakNode parse_break(char* src, int32_t start);
ContinueNode parse_continue(char* src, int32_t start);
ConstNode parse_const(char* src, int32_t start);
ParseResult collect_until_semi(char* src, int32_t start);
ParseResult collect_until_brace(char* src, int32_t start);
FieldNode parse_field(char* src, int32_t start);
TypeDeclNode parse_typedecl(char* src, int32_t start);
EnumNode parse_enum(char* src, int32_t start);
SliceDeclNode parse_slice_decl(char* src, int32_t start);
StmtResult parse_stmt(char* src, int32_t start);
ProcNode parse_proc(char* src, int32_t start);
char* extract_lambdas(char* src);
ProgramParts parse_program_defs(char* src, char* alias, stkt_slice_str synced_files);
char* parse_program(char* src);




char* get_runtime_headers() {
        char* out = "";
        out = stkt_str_concat(out, "#include <stdio.h>\n");
        out = stkt_str_concat(out, "#include <stdlib.h>\n");
        out = stkt_str_concat(out, "#include <stdint.h>\n");
        out = stkt_str_concat(out, "#include <stdbool.h>\n");
        out = stkt_str_concat(out, "#include <string.h>\n");
        out = stkt_str_concat(out, "#include <math.h>\n");
        out = stkt_str_concat(out, "#include <stdarg.h>\n");
        out = stkt_str_concat(out, "#include <ctype.h>\n");
        out = stkt_str_concat(out, "#include <sys/time.h>\n");
        out = stkt_str_concat(out, "#include <unistd.h>\n");
        return out;
}

char* get_runtime_core() {
        char* out = "";
        out = stkt_str_concat(out, "static int __attribute__((unused)) __stkt_argc = 0;\n");
        out = stkt_str_concat(out, "static char** __attribute__((unused)) __stkt_argv = NULL;\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void stkt_exit(int32_t code) { exit(code); }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) int32_t stkt_scan_i32() { int32_t v=0; if (scanf(\"%d\", &v) != 1) return 0; return v; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) double stkt_scan_f64() { double v=0; if (scanf(\"%lf\", &v) != 1) return 0; return v; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* stkt_scan_str() { char* b = (char*)malloc(1024); if (!b) return \"\"; if (!fgets(b, 1024, stdin)) { b[0] = 0; return b; } size_t l = strlen(b); if (l > 0 && b[l-1] == '\\n') b[l-1] = 0; if (l > 1 && b[l-2] == '\\r') b[l-2] = 0; return b; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) bool stkt_scan_bool() { char b[16]; if (scanf(\"%15s\", b) != 1) return false; return (strcmp(b, \"true\") == 0 || strcmp(b, \"1\") == 0); }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char stkt_scan_char() { char c = 0; if (scanf(\" %c\", &c) != 1) return 0; return c; }\n");
        out = stkt_str_concat(out, "typedef struct __stkt_arena_chunk { char* memory; size_t capacity; size_t offset; struct __stkt_arena_chunk* next; } __stkt_arena_chunk;\n");
        out = stkt_str_concat(out, "typedef struct { __stkt_arena_chunk* current; size_t default_chunk_size; } __stkt_arena;\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) int64_t stkt_arena_create(int32_t chunk_size) { if (chunk_size <= 0) chunk_size = 65536; __stkt_arena* a = (__stkt_arena*)malloc(sizeof(__stkt_arena)); a->default_chunk_size = (size_t)chunk_size; __stkt_arena_chunk* c = (__stkt_arena_chunk*)malloc(sizeof(__stkt_arena_chunk)); c->memory = (char*)malloc((size_t)chunk_size); c->capacity = (size_t)chunk_size; c->offset = 0; c->next = NULL; a->current = c; return (int64_t)(uintptr_t)a; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void* stkt_arena_alloc(__stkt_arena* a, size_t size) { if (!a) return NULL; size = (size + 7) & ~7; __stkt_arena_chunk* c = a->current; if (c->offset + size > c->capacity) { size_t new_cap = a->default_chunk_size; if (size > new_cap) new_cap = size; __stkt_arena_chunk* nc = (__stkt_arena_chunk*)malloc(sizeof(__stkt_arena_chunk)); nc->memory = (char*)malloc(new_cap); nc->capacity = new_cap; nc->offset = 0; nc->next = c; a->current = nc; c = nc; } void* ptr = (void*)(c->memory + c->offset); c->offset += size; return ptr; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* stkt_arena_alloc_str(int64_t handle, const char* s) { __stkt_arena* a = (__stkt_arena*)(uintptr_t)handle; if (!a || !s) return \"\"; size_t len = strlen(s); char* dest = (char*)stkt_arena_alloc(a, len + 1); if (!dest) return \"\"; memcpy(dest, s, len); dest[len] = 0; return dest; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void stkt_arena_reset(int64_t handle) { __stkt_arena* a = (__stkt_arena*)(uintptr_t)handle; if (!a) return; __stkt_arena_chunk* c = a->current; while (c) { c->offset = 0; c = c->next; } }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void stkt_arena_destroy(int64_t handle) { __stkt_arena* a = (__stkt_arena*)(uintptr_t)handle; if (!a) return; __stkt_arena_chunk* c = a->current; while (c) { __stkt_arena_chunk* next = c->next; if (c->memory) free(c->memory); free(c); c = next; } free(a); }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* stkt_format(const char* fmt, ...) { va_list args, args2; va_start(args, fmt); va_copy(args2, args); int len = vsnprintf(NULL, 0, fmt, args); va_end(args); if (len < 0) { va_end(args2); return \"\"; } char* b = (char*)malloc((size_t)len + 1); if (!b) { va_end(args2); return \"\"; } vsnprintf(b, (size_t)len + 1, fmt, args2); va_end(args2); return b; }\n");
        return out;
}

char* get_runtime_slices() {
        char* out = "";
        out = stkt_str_concat(out, "#define STKT_SLICE_DEFINE(TYPE, NAME) typedef struct { TYPE* data; size_t len; size_t cap; } __stkt_slice_buf_##NAME; typedef struct { __stkt_slice_buf_##NAME* buf; } NAME;\n");
        out = stkt_str_concat(out, "STKT_SLICE_DEFINE(int32_t, stkt_slice_i32)\n");
        out = stkt_str_concat(out, "STKT_SLICE_DEFINE(int64_t, stkt_slice_i64)\n");
        out = stkt_str_concat(out, "STKT_SLICE_DEFINE(float, stkt_slice_f32)\n");
        out = stkt_str_concat(out, "STKT_SLICE_DEFINE(double, stkt_slice_f64)\n");
        out = stkt_str_concat(out, "STKT_SLICE_DEFINE(char*, stkt_slice_str)\n");
        out = stkt_str_concat(out, "#define STKT_SLICE_INIT(s) do { (s).buf = malloc(sizeof(*((s).buf))); (s).buf->data = NULL; (s).buf->len = 0; (s).buf->cap = 0; } while(0)\n");
        out = stkt_str_concat(out, "#define STKT_SLICE_APPEND(s, val) do { if ((s).buf->len >= (s).buf->cap) { (s).buf->cap = ((s).buf->cap == 0) ? 4 : ((s).buf->cap * 2); (s).buf->data = realloc((s).buf->data, (s).buf->cap * sizeof(*((s).buf->data))); } (s).buf->data[(s).buf->len++] = (val); } while(0)\n");
        out = stkt_str_concat(out, "#define STKT_SLICE_POP(s) ((s).buf->data[--((s).buf->len)])\n");
        out = stkt_str_concat(out, "#define STKT_SLICE_LEN(s) ((int32_t)((s).buf->len))\n");
        return out;
}

char* get_runtime_error() {
        char* out = "";
        out = stkt_str_concat(out, "static bool __attribute__((unused)) __stkt_has_error = false;\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void __stkt_set_err() { __stkt_has_error = true; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void __stkt_clear_err() { __stkt_has_error = false; }\n");
        return out;
}

char* get_runtime_strings() {
        char* out = "";
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* stkt_str_concat(const char* s1, const char* s2) { if (!s1) s1 = \"\"; if (!s2) s2 = \"\"; size_t l1 = strlen(s1); size_t l2 = strlen(s2); char* r = (char*)malloc(l1 + l2 + 1); if (!r) return \"\"; memcpy(r, s1, l1); memcpy(r + l1, s2, l2); r[l1 + l2] = 0; return r; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* stkt_str_slice(const char* s, int32_t start, int32_t end) { if (!s) return \"\"; int32_t l = (int32_t)strlen(s); if (start < 0) start = 0; if (end > l) end = l; if (start >= end) { char* e = (char*)malloc(1); e[0] = 0; return e; } int32_t sub_len = end - start; char* r = (char*)malloc(sub_len + 1); if (!r) return \"\"; memcpy(r, s + start, sub_len); r[sub_len] = 0; return r; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) stkt_slice_str stkt_str_split(const char* s, const char* sep) { stkt_slice_str res; STKT_SLICE_INIT(res); if (!s || !sep) return res; size_t sl = strlen(sep); if (sl == 0) { STKT_SLICE_APPEND(res, strdup(s)); return res; } const char* curr = s; const char* found; while ((found = strstr(curr, sep)) != NULL) { size_t pl = found - curr; char* p = (char*)malloc(pl + 1); memcpy(p, curr, pl); p[pl] = 0; STKT_SLICE_APPEND(res, p); curr = found + sl; } STKT_SLICE_APPEND(res, strdup(curr)); return res; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* stkt_str_trim(const char* s) { if (!s) return \"\"; while (isspace((unsigned char)*s)) s++; if (*s == 0) return strdup(\"\"); const char* end = s + strlen(s) - 1; while (end > s && isspace((unsigned char)*end)) end--; size_t l = end - s + 1; char* r = (char*)malloc(l + 1); memcpy(r, s, l); r[l] = 0; return r; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) bool stkt_str_contains(const char* s, const char* sub) { if (!s || !sub) return false; return strstr(s, sub) != NULL; }\n");
        return out;
}

char* get_runtime_io() {
        char* out = "";
        out = stkt_str_concat(out, "static inline __attribute__((unused)) bool stkt_file_exists(const char* path) { if (!path) return false; FILE* f = fopen(path, \"r\"); if (f) { fclose(f); return true; } return false; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) bool stkt_file_write(const char* path, const char* content) { if (!path) return false; FILE* f = fopen(path, \"w\"); if (!f) return false; fputs(content ? content : \"\", f); fclose(f); return true; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) bool stkt_file_append(const char* path, const char* content) { if (!path) return false; FILE* f = fopen(path, \"a\"); if (!f) return false; fputs(content ? content : \"\", f); fclose(f); return true; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) int32_t stkt_file_size(const char* path) { if (!path) return -1; FILE* f = fopen(path, \"rb\"); if (!f) return -1; fseek(f, 0, SEEK_END); long s = ftell(f); fclose(f); return (int32_t)s; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* stkt_file_read(const char* path) { if (!path) return \"\"; FILE* f = fopen(path, \"rb\"); if (!f) return \"\"; fseek(f, 0, SEEK_END); long s = ftell(f); fseek(f, 0, SEEK_SET); char* b = (char*)malloc(s + 1); if (!b) { fclose(f); return \"\"; } size_t r = fread(b, 1, s, f); b[r] = 0; fclose(f); return b; }\n");
        return out;
}

char* get_runtime_hmap() {
        char* out = "";
        out = stkt_str_concat(out, "typedef struct __stkt_map_entry_str_i32 { char* key; int32_t val; struct __stkt_map_entry_str_i32* next; } __stkt_map_entry_str_i32;\n");
        out = stkt_str_concat(out, "typedef struct { __stkt_map_entry_str_i32* buckets[64]; int32_t size; } __stkt_map_str_i32;\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) uint32_t __stkt_hash_str(const char* s) { uint32_t h = 2166136261u; if (!s) return 0; while (*s) { h ^= (uint8_t)*s++; h *= 16777619u; } return h; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) __stkt_map_str_i32* __stkt_map_create_str_i32() { return (__stkt_map_str_i32*)calloc(1, sizeof(__stkt_map_str_i32)); }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void __stkt_map_set_str_i32(__stkt_map_str_i32* m, const char* key, int32_t val) { if (!m || !key) return; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { curr->val = val; return; } curr = curr->next; } __stkt_map_entry_str_i32* entry = (__stkt_map_entry_str_i32*)malloc(sizeof(__stkt_map_entry_str_i32)); entry->key = strdup(key); entry->val = val; entry->next = m->buckets[idx]; m->buckets[idx] = entry; m->size++; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) int32_t __stkt_map_get_str_i32(__stkt_map_str_i32* m, const char* key) { if (!m || !key) { __stkt_set_err(); return 0; } uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { return curr->val; } curr = curr->next; } __stkt_set_err(); return 0; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) bool __stkt_map_has_str_i32(__stkt_map_str_i32* m, const char* key) { if (!m || !key) return false; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_i32* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) return true; curr = curr->next; } return false; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) stkt_slice_str __stkt_map_keys_str_i32(__stkt_map_str_i32* m) { stkt_slice_str res; STKT_SLICE_INIT(res); if (!m) return res; for (int i = 0; i < 64; i++) { __stkt_map_entry_str_i32* curr = m->buckets[i]; while (curr) { STKT_SLICE_APPEND(res, curr->key); curr = curr->next; } } return res; }\n");
        out = stkt_str_concat(out, "typedef struct __stkt_map_entry_str_str { char* key; char* val; struct __stkt_map_entry_str_str* next; } __stkt_map_entry_str_str;\n");
        out = stkt_str_concat(out, "typedef struct { __stkt_map_entry_str_str* buckets[64]; int32_t size; } __stkt_map_str_str;\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) __stkt_map_str_str* __stkt_map_create_str_str() { return (__stkt_map_str_str*)calloc(1, sizeof(__stkt_map_str_str)); }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void __stkt_map_set_str_str(__stkt_map_str_str* m, const char* key, const char* val) { if (!m || !key) return; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_str* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { if (curr->val) free(curr->val); curr->val = val ? strdup(val) : strdup(\"\"); return; } curr = curr->next; } __stkt_map_entry_str_str* entry = (__stkt_map_entry_str_str*)malloc(sizeof(__stkt_map_entry_str_str)); entry->key = strdup(key); entry->val = val ? strdup(val) : strdup(\"\"); entry->next = m->buckets[idx]; m->buckets[idx] = entry; m->size++; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* __stkt_map_get_str_str(__stkt_map_str_str* m, const char* key) { if (!m || !key) { __stkt_set_err(); return \"\"; } uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_str* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) { return curr->val; } curr = curr->next; } __stkt_set_err(); return \"\"; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) bool __stkt_map_has_str_str(__stkt_map_str_str* m, const char* key) { if (!m || !key) return false; uint32_t idx = __stkt_hash_str(key) % 64; __stkt_map_entry_str_str* curr = m->buckets[idx]; while (curr) { if (strcmp(curr->key, key) == 0) return true; curr = curr->next; } return false; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) stkt_slice_str __stkt_map_keys_str_str(__stkt_map_str_str* m) { stkt_slice_str res; STKT_SLICE_INIT(res); if (!m) return res; for (int i = 0; i < 64; i++) { __stkt_map_entry_str_str* curr = m->buckets[i]; while (curr) { STKT_SLICE_APPEND(res, curr->key); curr = curr->next; } } return res; }\n");
        return out;
}

char* get_runtime_os() {
        char* out = "";
        out = stkt_str_concat(out, "static inline __attribute__((unused)) int32_t stkt_args_count() { return (int32_t)__stkt_argc; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) stkt_slice_str stkt_get_args() { stkt_slice_str args; STKT_SLICE_INIT(args); for (int i = 0; i < __stkt_argc; i++) { STKT_SLICE_APPEND(args, __stkt_argv[i]); } return args; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) char* stkt_get_env(const char* key) { if (!key) return \"\"; char* v = getenv(key); return v ? v : (char*)\"\"; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) int32_t stkt_system(const char* cmd) { if (!cmd) return -1; return system(cmd); }\n");
        return out;
}

char* get_runtime_time() {
        char* out = "";
        out = stkt_str_concat(out, "static inline __attribute__((unused)) int64_t stkt_time_now_ms() { struct timeval tv; gettimeofday(&tv, NULL); return ((int64_t)tv.tv_sec * 1000) + (tv.tv_usec / 1000); }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) int64_t stkt_time_now_us() { struct timeval tv; gettimeofday(&tv, NULL); return ((int64_t)tv.tv_sec * 1000000) + tv.tv_usec; }\n");
        out = stkt_str_concat(out, "static inline __attribute__((unused)) void stkt_time_sleep_ms(int32_t ms) { if (ms > 0) usleep((useconds_t)ms * 1000); }\n");
        return out;
}

char* get_full_runtime() {
        char* r1 = get_runtime_core();
        char* r2 = get_runtime_slices();
        char* r3 = get_runtime_error();
        char* r4 = get_runtime_strings();
        char* r5 = get_runtime_io();
        char* r6 = get_runtime_hmap();
        char* r7 = get_runtime_os();
        char* r8 = get_runtime_time();
        return stkt_format("%s%s%s%s%s%s%s%s", r1, r2, r3, r4, r5, r6, r7, r8);
}


bool is_digit(char c) {
        if (c >= '0' && c <= '9') {
        return true;
    }
        return false;
}

bool is_alpha(char c) {
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c == '_')) {
        return true;
    }
        return false;
}

bool is_primitive_type(char* word) {
        if ((strcmp(word, "i8") == 0) || (strcmp(word, "i16") == 0) || (strcmp(word, "i32") == 0) || (strcmp(word, "i64") == 0)) {
        return true;
    }
        if ((strcmp(word, "u8") == 0) || (strcmp(word, "u16") == 0) || (strcmp(word, "u32") == 0) || (strcmp(word, "u64") == 0)) {
        return true;
    }
        if ((strcmp(word, "f32") == 0) || (strcmp(word, "f64") == 0) || (strcmp(word, "bool") == 0) || (strcmp(word, "str") == 0) || (strcmp(word, "char") == 0)) {
        return true;
    }
        if ((strcmp(word, "int") == 0) || (strcmp(word, "float") == 0)) {
        return true;
    }
        return false;
}

int32_t skip_whitespace(char* src, int32_t start) {
        int32_t p = start;
        int32_t n = ((int32_t)strlen(src));
        while (p < n) {
        char ch = src[p];
        if (ch == ' ' || ch == '\t' || ch == '\n' || ch == '\r') {
        p = p + 1;
    } else {
        if (ch == '/' && p + 1 < n && src[p + 1] == '/') {
        p = p + 2;
        while (p < n && src[p] != '\n') {
        p = p + 1;
    }
    } else {
        return p;
    }
    }
    }
        return p;
}

TokenKind check_keyword(char* word) {
        if ((strcmp(word, "let") == 0)) {
        return TokenKind_TokLet;
    }
        if ((strcmp(word, "fn") == 0)) {
        return TokenKind_TokProc;
    }
        if ((strcmp(word, "if") == 0)) {
        return TokenKind_TokIf;
    }
        if ((strcmp(word, "else") == 0)) {
        return TokenKind_TokElse;
    }
        if ((strcmp(word, "while") == 0)) {
        return TokenKind_TokWhile;
    }
        if ((strcmp(word, "return") == 0)) {
        return TokenKind_TokReturn;
    }
        if ((strcmp(word, "onscreen") == 0)) {
        return TokenKind_TokOnscreen;
    }
        if ((strcmp(word, "break") == 0)) {
        return TokenKind_TokBreak;
    }
        if ((strcmp(word, "continue") == 0)) {
        return TokenKind_TokContinue;
    }
        if ((strcmp(word, "const") == 0)) {
        return TokenKind_TokConst;
    }
        if ((strcmp(word, "onkey") == 0)) {
        return TokenKind_TokOnkey;
    }
        if ((strcmp(word, "for") == 0)) {
        return TokenKind_TokFor;
    }
        if ((strcmp(word, "loop") == 0)) {
        return TokenKind_TokLoop;
    }
        if ((strcmp(word, "step") == 0)) {
        return TokenKind_TokStep;
    }
        if ((strcmp(word, "in") == 0)) {
        return TokenKind_TokIn;
    }
        if ((strcmp(word, "match") == 0)) {
        return TokenKind_TokMatch;
    }
        if ((strcmp(word, "case") == 0)) {
        return TokenKind_TokCase;
    }
        if ((strcmp(word, "default") == 0)) {
        return TokenKind_TokDefault;
    }
        if ((strcmp(word, "L") == 0)) {
        return TokenKind_TokLambda;
    }
        if ((strcmp(word, "true") == 0)) {
        return TokenKind_TokTrue;
    }
        if ((strcmp(word, "false") == 0)) {
        return TokenKind_TokFalse;
    }
        if ((strcmp(word, "type") == 0)) {
        return TokenKind_TokType;
    }
        if ((strcmp(word, "enum") == 0)) {
        return TokenKind_TokEnum;
    }
        if ((strcmp(word, "pop") == 0)) {
        return TokenKind_TokPop;
    }
        if ((strcmp(word, "len") == 0)) {
        return TokenKind_TokLen;
    }
        if ((strcmp(word, "append") == 0)) {
        return TokenKind_TokAppend;
    }
        if ((strcmp(word, "hmap") == 0)) {
        return TokenKind_TokHMap;
    }
        if ((strcmp(word, "incl") == 0)) {
        return TokenKind_TokSync;
    }
        if ((strcmp(word, "export") == 0)) {
        return TokenKind_TokExport;
    }
        if ((strcmp(word, "as") == 0)) {
        return TokenKind_TokAs;
    }
        return TokenKind_TokIdent;
}

Token next_token(char* src, int32_t start) {
        int32_t p = skip_whitespace(src, start);
        int32_t n = ((int32_t)strlen(src));
        if (p >= n) {
        return (Token){TokenKind_TokEof, 0, 0.0, "", p, 1};
    }
        char ch = src[p];
        char quote_char = '"';
        char chr_char = ((char)(39));
        char esc_char = '\\';
        if (ch == quote_char) {
        int32_t str_start = p;
        p = p + 1;
        while (p < n && src[p] != quote_char) {
        if (src[p] == esc_char && p + 1 < n) {
        p = p + 2;
    } else {
        p = p + 1;
    }
    }
        if (p < n && src[p] == quote_char) {
        p = p + 1;
    }
        char* str_literal = stkt_str_slice(src, str_start, p);
        return (Token){TokenKind_TokStr, 0, 0.0, str_literal, p, 1};
    }
        if (ch == chr_char) {
        int32_t chr_start = p;
        p = p + 1;
        while (p < n && src[p] != chr_char) {
        if (src[p] == esc_char && p + 1 < n) {
        p = p + 2;
    } else {
        p = p + 1;
    }
    }
        if (p < n && src[p] == chr_char) {
        p = p + 1;
    }
        char* chr_literal = stkt_str_slice(src, chr_start, p);
        return (Token){TokenKind_TokChar, 0, 0.0, chr_literal, p, 1};
    }
        if (is_digit(ch)) {
        int32_t num_start = p;
        int32_t num = 0;
        while (p < n && is_digit(src[p])) {
        num = (num * 10) + (src[p] - '0');
        p = p + 1;
    }
        if (p < n && src[p] == '.' && (p + 1 < n && is_digit(src[p + 1]))) {
        p = p + 1;
        float frac = 0.0;
        float place = 0.1;
        while (p < n && is_digit(src[p])) {
        float d_val = ((float)((src[p] - '0')));
        frac = frac + (d_val * place);
        place = place * 0.1;
        p = p + 1;
    }
        float f_num = ((float)(num));
        float fval = f_num + frac;
        char* float_str = stkt_str_slice(src, num_start, p);
        return (Token){TokenKind_TokFloat, 0, fval, float_str, p, 1};
    }
        char* num_str = stkt_str_slice(src, num_start, p);
        return (Token){TokenKind_TokInt, num, 0.0, num_str, p, 1};
    }
        if (is_alpha(ch)) {
        int32_t word_start = p;
        while (p < n && (is_alpha(src[p]) || is_digit(src[p]))) {
        p = p + 1;
    }
        char* word = stkt_str_slice(src, word_start, p);
        if ((strcmp(word, "isok") == 0) && p < n && src[p] == '?') {
        p = p + 1;
        return (Token){TokenKind_TokIsok, 0, 0.0, stkt_str_concat("isok", "?"), p, 1};
    }
        TokenKind kind = check_keyword(word);
        return (Token){kind, 0, 0.0, word, p, 1};
    }
        if (p + 1 < n) {
        char next_ch = src[p + 1];
        if (ch == '=' && next_ch == '=') {
        return (Token){TokenKind_TokEq, 0, 0.0, "==", p + 2, 1};
    }
        if (ch == '!' && next_ch == '=') {
        return (Token){TokenKind_TokNe, 0, 0.0, "!=", p + 2, 1};
    }
        if (ch == '<' && next_ch == '=') {
        return (Token){TokenKind_TokLe, 0, 0.0, "<=", p + 2, 1};
    }
        if (ch == '>' && next_ch == '=') {
        return (Token){TokenKind_TokGe, 0, 0.0, ">=", p + 2, 1};
    }
        if (ch == '&' && next_ch == '&') {
        return (Token){TokenKind_TokAnd, 0, 0.0, "&&", p + 2, 1};
    }
        if (ch == '|' && next_ch == '|') {
        return (Token){TokenKind_TokOr, 0, 0.0, "||", p + 2, 1};
    }
    }
        if (ch == '+') {
        return (Token){TokenKind_TokPlus, 0, 0.0, "+", p + 1, 1};
    }
        if (ch == '-') {
        return (Token){TokenKind_TokMinus, 0, 0.0, "-", p + 1, 1};
    }
        if (ch == '*') {
        return (Token){TokenKind_TokStar, 0, 0.0, "*", p + 1, 1};
    }
        if (ch == '/') {
        return (Token){TokenKind_TokSlash, 0, 0.0, "/", p + 1, 1};
    }
        if (ch == '=') {
        return (Token){TokenKind_TokAssign, 0, 0.0, "=", p + 1, 1};
    }
        if (ch == '<') {
        return (Token){TokenKind_TokLt, 0, 0.0, "<", p + 1, 1};
    }
        if (ch == '>') {
        return (Token){TokenKind_TokGt, 0, 0.0, ">", p + 1, 1};
    }
        if (ch == '!') {
        return (Token){TokenKind_TokNot, 0, 0.0, "!", p + 1, 1};
    }
        if (ch == ':') {
        return (Token){TokenKind_TokColon, 0, 0.0, ":", p + 1, 1};
    }
        if (ch == ',') {
        return (Token){TokenKind_TokComma, 0, 0.0, ",", p + 1, 1};
    }
        if (ch == ';') {
        return (Token){TokenKind_TokSemicolon, 0, 0.0, ";", p + 1, 1};
    }
        if (ch == '(') {
        return (Token){TokenKind_TokLParen, 0, 0.0, "(", p + 1, 1};
    }
        if (ch == ')') {
        return (Token){TokenKind_TokRParen, 0, 0.0, ")", p + 1, 1};
    }
        if (ch == '{') {
        return (Token){TokenKind_TokLBrace, 0, 0.0, "{", p + 1, 1};
    }
        if (ch == '}') {
        return (Token){TokenKind_TokRBrace, 0, 0.0, "}", p + 1, 1};
    }
        if (ch == '[') {
        return (Token){TokenKind_TokLBracket, 0, 0.0, "[", p + 1, 1};
    }
        if (ch == ']') {
        return (Token){TokenKind_TokRBracket, 0, 0.0, "]", p + 1, 1};
    }
        if (ch == '?') {
        return (Token){TokenKind_TokQuestion, 0, 0.0, "?", p + 1, 1};
    }
        if (ch == '.') {
        return (Token){TokenKind_TokDot, 0, 0.0, ".", p + 1, 1};
    }
        if (ch == '_') {
        return (Token){TokenKind_TokDefault, 0, 0.0, "_", p + 1, 1};
    }
        return (Token){TokenKind_TokEof, 0, 0.0, "", p + 1, 1};
}


char* to_c_type(char* stkt_t) {
        if (((int32_t)strlen(stkt_t)) >= 3 && stkt_t[0] == '[' && stkt_t[((int32_t)strlen(stkt_t)) - 1] == ']') {
        char* elem_t = stkt_str_slice(stkt_t, 1, (((int32_t)strlen(stkt_t)) - 1));
        return stkt_format("stkt_slice_%s", elem_t);
    }
        if ((strcmp(stkt_t, "i8") == 0)) {
        return "int8_t";
    }
        if ((strcmp(stkt_t, "i16") == 0)) {
        return "int16_t";
    }
        if ((strcmp(stkt_t, "i32") == 0)) {
        return "int32_t";
    }
        if ((strcmp(stkt_t, "i64") == 0)) {
        return "int64_t";
    }
        if ((strcmp(stkt_t, "u8") == 0)) {
        return "uint8_t";
    }
        if ((strcmp(stkt_t, "u16") == 0)) {
        return "uint16_t";
    }
        if ((strcmp(stkt_t, "u32") == 0)) {
        return "uint32_t";
    }
        if ((strcmp(stkt_t, "u64") == 0)) {
        return "uint64_t";
    }
        if ((strcmp(stkt_t, "f32") == 0)) {
        return "float";
    }
        if ((strcmp(stkt_t, "f64") == 0)) {
        return "double";
    }
        if ((strcmp(stkt_t, "bool") == 0)) {
        return "bool";
    }
        if ((strcmp(stkt_t, "str") == 0)) {
        return "char*";
    }
        if ((strcmp(stkt_t, "void") == 0)) {
        return "void";
    }
        return stkt_t;
}

RuntimeFeatures detect_features(char* code) {
        bool f_strings = stkt_str_contains(code, "stkt_str_") || stkt_str_contains(code, ".trim(") || stkt_str_contains(code, ".split(") || stkt_str_contains(code, ".contains(");
        bool f_hmap = stkt_str_contains(code, "__stkt_map_") || stkt_str_contains(code, "hmap[");
        bool f_error = stkt_str_contains(code, "__stkt_") || stkt_str_contains(code, "isok?") || stkt_str_contains(code, ".or(") || f_hmap;
        bool f_slices = stkt_str_contains(code, "stkt_slice_") || stkt_str_contains(code, "STKT_SLICE_") || stkt_str_contains(code, "append(") || stkt_str_contains(code, "pop(") || stkt_str_contains(code, "len(") || f_hmap || f_strings;
        bool f_io = stkt_str_contains(code, "stkt_file_") || stkt_str_contains(code, "file_exists") || stkt_str_contains(code, "read_text") || stkt_str_contains(code, "write_text") || stkt_str_contains(code, "append_text") || stkt_str_contains(code, "file_size");
        bool f_os = stkt_str_contains(code, "stkt_args_") || stkt_str_contains(code, "stkt_get_args") || stkt_str_contains(code, "stkt_get_env") || stkt_str_contains(code, "arg_count") || stkt_str_contains(code, "get_args");
        bool f_time = stkt_str_contains(code, "stkt_time_") || stkt_str_contains(code, "time_now") || stkt_str_contains(code, "time_sleep");
        return (RuntimeFeatures){f_slices, f_strings, f_hmap, f_io, f_os, f_error, f_time};
}

char* gen_let(LetNode node) {
        char* id = node.name;
        char* val = node.val;
        char* t = node.type_name;
        if (((int32_t)strlen(val)) >= 9 && val[0] == '_' && val[1] == '_' && val[2] == 'l' && val[3] == 'a' && val[4] == 'm' && val[5] == 'b' && val[6] == 'd' && val[7] == 'a' && val[8] == '_') {
        return stkt_format("    __auto_type %s = %s;", id, val);
    }
        if (((int32_t)strlen(t)) >= 4 && t[0] == 's' && t[1] == 't' && t[2] == 'r' && t[3] == '[') {
        return stkt_format("    char %s[] = %s;", id, val);
    }
        char* c_t = to_c_type(t);
        return stkt_format("    %s %s = %s;", c_t, id, val);
}

char* gen_assign(AssignNode node) {
        char* id = node.name;
        char* val = node.val;
        return stkt_format("    %s = %s;", id, val);
}

char* gen_if(IfNode node) {
        char* cond = node.cond;
        char* b = node.body;
        if (((int32_t)strlen(node.else_body)) > 0) {
        char* eb = node.else_body;
        return stkt_format("    if (%s) {\n%s    } else {\n%s    }", cond, b, eb);
    }
        return stkt_format("    if (%s) {\n%s    }", cond, b);
}

char* gen_while(WhileNode node) {
        char* cond = node.cond;
        char* b = node.body;
        return stkt_format("    while (%s) {\n%s    }", cond, b);
}

char* gen_print(PrintNode node) {
        char* val = node.val;
        char* t = node.type_name;
        if ((strcmp(t, "bool") == 0)) {
        return stkt_format("    printf(\"%%s\\n\", (%s) ? \"true\" : \"false\");", val);
    }
        if ((strcmp(t, "f32") == 0) || (strcmp(t, "f64") == 0) || (strcmp(t, "float") == 0)) {
        return stkt_format("    printf(\"%%f\\n\", %s);", val);
    }
        if ((strcmp(t, "str") == 0)) {
        return stkt_format("    printf(\"%%s\\n\", %s);", val);
    }
        if ((strcmp(t, "char") == 0)) {
        return stkt_format("    printf(\"%%c\\n\", %s);", val);
    }
        if (((int32_t)strlen(val)) >= 2 && (strcmp(stkt_str_slice(val, 0, 1), "\"") == 0)) {
        return stkt_format("    printf(\"%%s\\n\", %s);", val);
    }
        if (((int32_t)strlen(val)) >= 3 && (strcmp(stkt_str_slice(val, 0, 1), "'") == 0)) {
        return stkt_format("    printf(\"%%c\\n\", %s);", val);
    }
        if ((strcmp(val, "true") == 0) || (strcmp(val, "false") == 0)) {
        return stkt_format("    printf(\"%%s\\n\", (%s) ? \"true\" : \"false\");", val);
    }
        if (((int32_t)strlen(val)) >= 2 && (strcmp(stkt_str_slice(val, 0, 2), "(!") == 0)) {
        return stkt_format("    printf(\"%%s\\n\", (%s) ? \"true\" : \"false\");", val);
    }
        if (((int32_t)strlen(val)) >= 2 && (strcmp(stkt_str_slice(val, 0, 2), "(-") == 0)) {
        return stkt_format("    printf(\"%%d\\n\", %s);", val);
    }
        if (((int32_t)strlen(val)) > 0 && val[0] >= '0' && val[0] <= '9' && stkt_str_contains(val, ".")) {
        return stkt_format("    printf(\"%%f\\n\", %s);", val);
    }
        return stkt_format("    printf(\"%%d\\n\", %s);", val);
}

char* gen_return(ReturnNode node) {
        if (((int32_t)strlen(node.val)) > 0) {
        return stkt_format("    return %s;", node.val);
    }
        return "    return;";
}

char* gen_proc(ProcNode node) {
        char* c_ret = to_c_type(node.ret_type);
        return stkt_format("%s %s(%s) {\n%s}\n", c_ret, node.name, node.params, node.body);
}

char* gen_break(BreakNode node) {
        return "    break;";
}

char* gen_continue(ContinueNode node) {
        return "    continue;";
}

char* gen_const(ConstNode node) {
        char* name = node.name;
        char* type_name = node.type_name;
        char* c_type = to_c_type(type_name);
        char* val = node.val;
        return stkt_format("    const %s %s = %s;", c_type, name, val);
}

char* gen_call(CallNode node) {
        char* name = node.name;
        char* args = node.args;
        return stkt_format("    %s(%s);", name, args);
}

char* gen_array_decl(ArrayDeclNode node) {
        char* name = node.name;
        char* size = node.size;
        char* type_str = node.type_name;
        char* c_type = to_c_type(type_str);
        char* elements = node.element;
        if (((int32_t)strlen(elements)) > 0) {
        return stkt_format("    %s %s[%s] = %s;", c_type, name, size, elements);
    }
        return stkt_format("    %s %s[%s];", c_type, name, size);
}

char* gen_index_assign(IndexAssignNode node) {
        char* name = node.name;
        char* index = node.index;
        char* val = node.val;
        return stkt_format("    %s[%s] = %s;", name, index, val);
}

char* gen_index_access(IndexAccessNode node) {
        char* name = node.name;
        char* index = node.index;
        return stkt_format("%s[%s]", name, index);
}

char* gen_cast(CastNode node) {
        char* c_type = to_c_type(node.target_type);
        return stkt_format("((%s)(%s))", c_type, node.val);
}

char* gen_interpolate(InterpolatedStrNode node) {
        char* fmt = node.fmt_str;
        char* args = node.arg_str;
        if (((int32_t)strlen(args)) > 0) {
        return stkt_format("stkt_format(%s, %s)", fmt, args);
    }
        return stkt_format("stkt_format(%s)", fmt);
}

char* gen_for(ForNode node) {
        char* init = node.init;
        char* cond = node.cond;
        char* iter = node.iter;
        char* b = node.body;
        return stkt_format("    for (%s; %s; %s) {\n%s    }", init, cond, iter, b);
}

char* gen_loop(LoopNode node) {
        char* times = node.times;
        char* s = node.step_val;
        char* b = node.body;
        return stkt_format("    for (int32_t i = 0; i < %s; i = i + %s) {\n%s    }", times, s, b);
}

char* gen_for_in(ForinNode node) {
        char* ident = node.ident;
        char* collection = node.collection;
        char* b = node.body;
        if (stkt_str_contains(collection, "keys")) {
        return stkt_format("    stkt_slice_str __iter_keys = %s;\n    for (int32_t __idx = 0; __idx < STKT_SLICE_LEN(__iter_keys); __idx++) {\n        char* %s = __iter_keys.buf->data[__idx];\n%s    }", collection, ident, b);
    }
        return stkt_format("    for (int32_t i = 0; i < len(%s); i = i + 1) {\n        __auto_type %s = %s[i];\n%s    }", collection, ident, collection, b);
}

char* gen_ternary(TernaryNode node) {
        char* cond = node.cond;
        char* true_str = node.true_block;
        char* false_str = node.false_block;
        return stkt_format("((%s) ? (%s) : (%s))", cond, true_str, false_str);
}

char* gen_unary(UnaryNode node) {
        char* operand = node.operand;
        char* ops = node.ops;
        return stkt_format("(%s%s)", ops, operand);
}

char* gen_lambda(LambdaNode node) {
        char* id = node.id;
        char* return_type = to_c_type(node.ret_type);
        char* params_str = node.params;
        char* b = node.body;
        return stkt_format("static %s __lambda_%s(%s) {\n%s}\n", return_type, id, params_str, b);
}

char* gen_case(CaseNode node) {
        char* b = node.body;
        if (node.is_default) {
        return stkt_format("        default: {\n%s            break;\n        }\n", b);
    }
        char* t = node.target;
        return stkt_format("        case %s: {\n%s            break;\n        }\n", t, b);
}

char* gen_match(MatchNode node) {
        char* cond = node.cond;
        char* cases_code = node.cases_code;
        return stkt_format("    switch (%s) {\n%s    }", cond, cases_code);
}

char* gen_field(FieldNode node) {
        char* type_str = node.type_name;
        char* ident = node.ident;
        return stkt_format("       %s %s;", type_str, ident);
}

bool is_struct_name(char* src, char* name) {
        if (is_primitive_type(name)) {
        return false;
    }
        if ((strcmp(name, "TokenKind") == 0)) {
        return false;
    }
        if (((int32_t)strlen(name)) > 0 && name[0] >= 'A' && name[0] <= 'Z') {
        return true;
    }
        char* query = stkt_format("type %s", name);
        return stkt_str_contains(src, query);
}

bool is_enum_name(char* src, char* name) {
        if ((strcmp(name, "TokenKind") == 0)) {
        return true;
    }
        char* query = stkt_format("enum %s", name);
        if (stkt_str_contains(src, query)) {
        return true;
    }
        if (((int32_t)strlen(name)) > 0 && name[0] >= 'A' && name[0] <= 'Z' && (!is_struct_name(src, name))) {
        return true;
    }
        return false;
}

bool is_module_name(char* src, char* name) {
        if ((strcmp(name, "math") == 0) || (strcmp(name, "io") == 0) || (strcmp(name, "time") == 0) || (strcmp(name, "os") == 0) || (strcmp(name, "json") == 0) || (strcmp(name, "string") == 0) || (strcmp(name, "collections") == 0) || (strcmp(name, "algo") == 0) || (strcmp(name, "set") == 0)) {
        return true;
    }
        char* query1 = stkt_format("incl \"%s\"", name);
        char* query2 = stkt_format("incl \"%s.stkt\"", name);
        char* query1_old = stkt_format("sync \"%s\"", name);
        char* query2_old = stkt_format("sync \"%s.stkt\"", name);
        char* query3 = stkt_format(" as %s ", name);
        char* query4 = stkt_format(" as %s\n", name);
        char* query5 = stkt_format("/%s.stkt\"", name);
        if (stkt_str_contains(src, query1) || stkt_str_contains(src, query2) || stkt_str_contains(src, query1_old) || stkt_str_contains(src, query2_old) || stkt_str_contains(src, query3) || stkt_str_contains(src, query4) || stkt_str_contains(src, query5)) {
        return true;
    }
        return false;
}

char* gen_typeaccess(char* src, TypeAccessNode node) {
        char* target = node.target;
        char* member = node.fields;
        if (is_enum_name(src, target) || is_module_name(src, target)) {
        return stkt_format("%s_%s", target, member);
    }
        return stkt_format("%s.%s", target, member);
}

char* gen_enum(EnumNode node) {
        char* ident = node.ident;
        char* variants = node.variants;
        return stkt_format("typedef enum {\n%s} %s;\n", variants, ident);
}

char* gen_enumaccess(EnumAccessNode node) {
        char* ident = node.ident;
        char* variant = node.variant;
        return stkt_format("%s_%s", ident, variant);
}

char* gen_typedecl(TypeDeclNode node) {
        char* ident = node.ident;
        char* fields = node.fields;
        return stkt_format("typedef struct {\n%s} %s;", fields, ident);
}

char* gen_scan(ScanNode node) {
        if ((strcmp(node.type_name, "str") == 0)) {
        return "stkt_scan_str()";
    }
        if ((strcmp(node.type_name, "i32") == 0) || (strcmp(node.type_name, "i16") == 0) || (strcmp(node.type_name, "i8") == 0)) {
        return "stkt_scan_i32()";
    }
        if ((strcmp(node.type_name, "f32") == 0) || (strcmp(node.type_name, "f64") == 0) || (strcmp(node.type_name, "float") == 0)) {
        return "stkt_scan_f64()";
    }
        if ((strcmp(node.type_name, "u8") == 0) || (strcmp(node.type_name, "u16") == 0) || (strcmp(node.type_name, "u32") == 0) || (strcmp(node.type_name, "u64") == 0)) {
        return "stkt_scan_u64()";
    }
        if ((strcmp(node.type_name, "bool") == 0)) {
        return "stkt_scan_bool()";
    }
        if ((strcmp(node.type_name, "char") == 0)) {
        return "stkt_scan_char()";
    }
        return "stkt_scan_i32()";
}

bool is_slice_var(char* src, char* name) {
        char* q1 = stkt_format("let %s: [", name);
        char* q2 = stkt_format("let %s : [", name);
        char* q3 = stkt_format("(%s: [", name);
        char* q4 = stkt_format(" %s: [", name);
        char* q5 = stkt_format(", %s: [", name);
        return stkt_str_contains(src, q1) || stkt_str_contains(src, q2) || stkt_str_contains(src, q3) || stkt_str_contains(src, q4) || stkt_str_contains(src, q5);
}

bool is_hmap_var(char* src, char* name) {
        char* q1 = stkt_format("let %s: hmap", name);
        char* q2 = stkt_format("%s: hmap", name);
        return stkt_str_contains(src, q1) || stkt_str_contains(src, q2);
}

bool is_hmap_str_str(char* src, char* name) {
        char* q1 = stkt_format("let %s: hmap[str: str]", name);
        char* q2 = stkt_format("let %s: hmap[str, str]", name);
        char* q3 = stkt_format("%s: hmap[str: str]", name);
        return stkt_str_contains(src, q1) || stkt_str_contains(src, q2) || stkt_str_contains(src, q3);
}

char* to_slice_c_type(char* elem_t) {
        if ((strcmp(elem_t, "i32") == 0)) {
        return "stkt_slice_i32";
    }
        if ((strcmp(elem_t, "i64") == 0)) {
        return "stkt_slice_i64";
    }
        if ((strcmp(elem_t, "f32") == 0) || (strcmp(elem_t, "float") == 0)) {
        return "stkt_slice_f32";
    }
        if ((strcmp(elem_t, "f64") == 0) || (strcmp(elem_t, "double") == 0)) {
        return "stkt_slice_f64";
    }
        if ((strcmp(elem_t, "str") == 0)) {
        return "stkt_slice_str";
    }
        return "stkt_slice_i32";
}

char* gen_slice_decl(SliceDeclNode node) {
        char* name = node.name;
        char* elem_t = node.elem_type;
        char* sl_type = to_slice_c_type(elem_t);
        char* elems = node.elements;
        char* out = stkt_format("    %s %s;\n    STKT_SLICE_INIT(%s);\n", sl_type, name, name);
        int32_t n = ((int32_t)strlen(elems));
        if (n == 0) {
        return out;
    }
        int32_t p = 0;
        while (p < n) {
        while (p < n && (elems[p] == ' ' || elems[p] == ',' || elems[p] == '{' || elems[p] == '}')) {
        p = p + 1;
    }
        if (p >= n) {
        break;
    }
        int32_t e_start = p;
        while (p < n && elems[p] != ',' && elems[p] != '}' && elems[p] != ' ') {
        p = p + 1;
    }
        char* e_val = stkt_str_slice(elems, e_start, p);
        if (((int32_t)strlen(e_val)) > 0) {
        out = stkt_format("%s    STKT_SLICE_APPEND(%s, %s);\n", out, name, e_val);
    }
    }
        return out;
}

char* gen_append(AppendNode node) {
        char* arr = node.arr;
        char* val = node.val;
        return stkt_format("    STKT_SLICE_APPEND(%s, %s);", arr, val);
}

char* gen_index_assign_slice(char* src, IndexAssignNode node) {
        char* name = node.name;
        char* index = node.index;
        char* val = node.val;
        if (is_slice_var(src, name)) {
        return stkt_format("    %s.buf->data[%s] = %s;", name, index, val);
    }
        return stkt_format("    %s[%s] = %s;", name, index, val);
}

char* gen_isok(IsOkNode node) {
        char* expr_val = node.expr;
        char* msg_val = node.msg;
        char* c_t = "__auto_type";
        if (((int32_t)strlen(node.type_name)) > 0) {
        c_t = to_c_type(node.type_name);
    }
        return stkt_format("({ %s __v = %s; if (__stkt_has_error) { fprintf(stderr, \"[Error]: %%s\\n\", %s); exit(1); } __v; })", c_t, expr_val, msg_val);
}

char* gen_or(OrNode node) {
        char* expr_val = node.expr;
        char* fallback_val = node.fallback;
        char* c_t = "__auto_type";
        if (((int32_t)strlen(node.type_name)) > 0) {
        c_t = to_c_type(node.type_name);
    }
        return stkt_format("({ %s __v = %s; if (__stkt_has_error) { __stkt_clear_err(); __v = %s; } __v; })", c_t, expr_val, fallback_val);
}

char* gen_headers() {
        return get_runtime_headers();
}

char* gen_runtime(RuntimeFeatures features) {
        char* rt = get_runtime_core();
        if (features.needs_error) {
        char* code_error = get_runtime_error();
        rt = stkt_format("%s%s\n", rt, code_error);
    }
        if (features.needs_slices) {
        char* code_slices = get_runtime_slices();
        rt = stkt_format("%s%s\n", rt, code_slices);
    }
        if (features.needs_strings) {
        char* code_strings = get_runtime_strings();
        rt = stkt_format("%s%s\n", rt, code_strings);
    }
        if (features.needs_hmap) {
        char* code_hmap = get_runtime_hmap();
        rt = stkt_format("%s%s\n", rt, code_hmap);
    }
        if (features.needs_io) {
        char* code_io = get_runtime_io();
        rt = stkt_format("%s%s\n", rt, code_io);
    }
        if (features.needs_os) {
        char* code_os = get_runtime_os();
        rt = stkt_format("%s%s\n", rt, code_os);
    }
        if (features.needs_time) {
        char* code_time = get_runtime_time();
        rt = stkt_format("%s%s\n", rt, code_time);
    }
        return rt;
}

char* gen_aliased_proc(ProcNode node, char* alias) {
        char* c_ret = to_c_type(node.ret_type);
        char* final_name = node.name;
        if (((int32_t)strlen(alias)) > 0) {
        final_name = stkt_format("%s_%s", alias, node.name);
    }
        return stkt_format("%s %s(%s) {\n%s}\n", c_ret, final_name, node.params, node.body);
}

char* gen_program(char* procs, char* main_body) {
        char* header = gen_headers();
        char* full_src = stkt_format("%s\n%s", procs, main_body);
        RuntimeFeatures features = detect_features(full_src);
        char* runtime = gen_runtime(features);
        char* main_wrapper = stkt_str_concat(stkt_str_concat("int main(int argc, char** argv) {\n    __stkt_argc = argc;\n    __stkt_argv = argv;\n", main_body), "    return 0;\n}\n");
        char* full = stkt_str_concat(stkt_str_concat(stkt_str_concat(header, runtime), procs), main_wrapper);
        return full;
}


bool file_exists(char* path) {
        return stkt_file_exists(path);
}

bool write_text(char* path, char* content) {
        return stkt_file_write(path, content);
}

char* read_text(char* path) {
        return stkt_file_read(path);
}

bool append_text(char* path, char* content) {
        return stkt_file_append(path, content);
}

int32_t file_size(char* path) {
        if (file_exists(path)) {
        return stkt_file_size(path);
    } else {
        return (-1);
    }
}


int32_t arg_count() {
        return stkt_args_count();
}

stkt_slice_str get_args() {
        return stkt_get_args();
}

char* get_env(char* key) {
        return stkt_get_env(key);
}

int32_t system_cmd(char* cmd) {
        return stkt_system(cmd);
}


bool is_already_sync(stkt_slice_str synced, char* file) {
        int32_t n = STKT_SLICE_LEN(synced);
        int32_t i = 0;
        while (i < n) {
        if ((strcmp(synced.buf->data[i], file) == 0)) {
        return true;
    }
        i = i + 1;
    }
        return false;
}

char* clean_module_path(char* raw) {
        char* s = raw;
        if (((int32_t)strlen(s)) >= 2 && s[0] == '"') {
        int32_t last_idx = ((int32_t)strlen(s)) - 1;
        s = stkt_str_slice(s, 1, last_idx);
    }
        if ((!stkt_str_contains(s, ".stkt"))) {
        if ((strcmp(s, "string") == 0) || (strcmp(s, "collections") == 0) || (strcmp(s, "algo") == 0) || (strcmp(s, "set") == 0) || (strcmp(s, "time") == 0) || (strcmp(s, "json") == 0) || (strcmp(s, "queue") == 0) || (strcmp(s, "stackt") == 0) || (strcmp(s, "io") == 0) || (strcmp(s, "os") == 0) || (strcmp(s, "math") == 0) || (strcmp(s, "memory") == 0) || (strcmp(s, "arena") == 0)) {
        return stkt_format("src/stdlib/%s.stkt", s);
    }
        return stkt_format("%s.stkt", s);
    }
        return s;
}

char* find_var_type(char* src, char* name) {
        if (((int32_t)strlen(name)) == 0) {
        return "";
    }
        int32_t n = ((int32_t)strlen(src));
        int32_t vn = ((int32_t)strlen(name));
        if (stkt_str_contains(name, "__stkt_map_get_str_i32")) {
        return "i32";
    }
        if (stkt_str_contains(name, "__stkt_map_get_str_str")) {
        return "str";
    }
        if (stkt_str_contains(name, "__stkt_map_has")) {
        return "bool";
    }
        if (((int32_t)strlen(name)) >= 4 && (strcmp(stkt_str_slice(name, 0, 4), "len(") == 0)) {
        return "i32";
    }
        if (((int32_t)strlen(name)) >= 14 && (strcmp(stkt_str_slice(name, 0, 14), "STKT_SLICE_LEN") == 0)) {
        return "i32";
    }
        if (((int32_t)strlen(name)) >= 14 && (strcmp(stkt_str_slice(name, 0, 14), "STKT_SLICE_POP") == 0)) {
        return "i32";
    }
        if (stkt_str_contains(name, ".buf->data")) {
        return "i32";
    }
        int32_t dot_pos = (-1);
        int32_t k = 0;
        while (k < vn) {
        if (name[k] == '.') {
        dot_pos = k;
    }
        k = k + 1;
    }
        if (dot_pos >= 0 && dot_pos + 1 < vn) {
        char* field_name = stkt_str_slice(name, dot_pos + 1, vn);
        char* f_query = stkt_format("%s:", field_name);
        int32_t f_qlen = ((int32_t)strlen(f_query));
        int32_t fi = 0;
        while (fi <= n - f_qlen) {
        if ((strcmp(stkt_str_slice(src, fi, fi + f_qlen), f_query) == 0)) {
        int32_t f_start = fi + f_qlen;
        while (f_start < n && (src[f_start] == ' ' || src[f_start] == '\t')) {
        f_start = f_start + 1;
    }
        int32_t f_end = f_start;
        while (f_end < n && src[f_end] != ' ' && src[f_end] != '\n' && src[f_end] != ',' && src[f_end] != '}') {
        f_end = f_end + 1;
    }
        return stkt_str_slice(src, f_start, f_end);
    }
        fi = fi + 1;
    }
    }
        int32_t i = 0;
        while (i < n) {
        bool is_let = false;
        bool is_const = false;
        bool is_param = false;
        int32_t kw_end = 0;
        if (i + 4 <= n && (strcmp(stkt_str_slice(src, i, i + 4), "let ") == 0)) {
        is_let = true;
        kw_end = i + 4;
    }
        if (i + 6 <= n && (strcmp(stkt_str_slice(src, i, i + 6), "const ") == 0)) {
        is_const = true;
        kw_end = i + 6;
    }
        if (src[i] == '(' || src[i] == ',') {
        int32_t p_start = i + 1;
        while (p_start < n && (src[p_start] == ' ' || src[p_start] == '\t')) {
        p_start = p_start + 1;
    }
        kw_end = p_start;
        is_param = true;
    }
        if (is_let || is_const || is_param) {
        int32_t name_start = kw_end;
        if (name_start + vn <= n) {
        char* candidate = stkt_str_slice(src, name_start, name_start + vn);
        if ((strcmp(candidate, name) == 0)) {
        int32_t after_name = name_start + vn;
        if (after_name < n && (strcmp(stkt_str_slice(src, after_name, after_name + 1), ":") == 0)) {
        int32_t type_start = after_name + 1;
        while (type_start < n && src[type_start] == ' ') {
        type_start = type_start + 1;
    }
        int32_t type_end = type_start;
        while (type_end < n && src[type_end] != ' ' && src[type_end] != '\n' && src[type_end] != '=' && src[type_end] != '[' && src[type_end] != ')' && src[type_end] != ',') {
        type_end = type_end + 1;
    }
        return stkt_str_slice(src, type_start, type_end);
    }
    }
    }
    }
        i = i + 1;
    }
        return "";
}

SyncNode parse_sync(char* src, int32_t start) {
        int32_t p = start;
        Token tok_sync = next_token(src, p);
        p = tok_sync.next_pos;
        Token tok_path = next_token(src, p);
        p = tok_path.next_pos;
        char* clean_path = clean_module_path(tok_path.text);
        char* alias = "";
        Token tok_peek = next_token(src, p);
        if (tok_peek.kind == TokenKind_TokAs || (strcmp(tok_peek.text, "as") == 0)) {
        p = tok_peek.next_pos;
        Token tok_alias = next_token(src, p);
        alias = tok_alias.text;
        p = tok_alias.next_pos;
    }
        return (SyncNode){clean_path, alias, p};
}

ParseResult parse_grouped_expr(char* src, int32_t start) {
        int32_t p = start;
        int32_t depth = 1;
        char* expr_str = "";
        bool has_expr = false;
        while (true) {
        Token tok = next_token(src, p);
        if (tok.kind == TokenKind_TokEof) {
        break;
    }
        if (tok.kind == TokenKind_TokLParen) {
        depth = depth + 1;
        if (has_expr) {
        expr_str = stkt_format("%s (", expr_str);
    }
        if ((!has_expr)) {
        expr_str = "(";
        has_expr = true;
    }
        p = tok.next_pos;
    }
        if (tok.kind == TokenKind_TokRParen) {
        depth = depth - 1;
        if (depth == 0) {
        p = tok.next_pos;
        break;
    }
        if (has_expr) {
        expr_str = stkt_format("%s )", expr_str);
    }
        if ((!has_expr)) {
        expr_str = ")";
        has_expr = true;
    }
        p = tok.next_pos;
    }
        if (tok.kind != TokenKind_TokLParen && tok.kind != TokenKind_TokRParen) {
        p = tok.next_pos;
        char* t_text = tok.text;
        if (tok.kind == TokenKind_TokIdent) {
        Token peek_dot = next_token(src, p);
        if (peek_dot.kind == TokenKind_TokDot) {
        p = peek_dot.next_pos;
        Token m_tok = next_token(src, p);
        p = m_tok.next_pos;
        if (is_enum_name(src, t_text)) {
        t_text = stkt_format("%s_%s", t_text, m_tok.text);
    }
        if (is_module_name(src, t_text)) {
        t_text = stkt_format("%s_%s", t_text, m_tok.text);
    }
        if ((!is_enum_name(src, t_text)) && (!is_module_name(src, t_text))) {
        t_text = stkt_format("%s.%s", t_text, m_tok.text);
    }
    }
    }
        if (has_expr) {
        expr_str = stkt_format("%s %s", expr_str, t_text);
    }
        if ((!has_expr)) {
        expr_str = t_text;
        has_expr = true;
    }
    }
    }
        return (ParseResult){stkt_format("(%s)", expr_str), p};
}

bool is_valid_interp_var(char* var_expr) {
        int32_t vn = ((int32_t)strlen(var_expr));
        if (vn == 0) {
        return false;
    }
        int32_t k = 0;
        while (k < vn) {
        char ch = var_expr[k];
        if ((!((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch == '_' || ch == '.'))) {
        return false;
    }
        k = k + 1;
    }
        return true;
}

ParseResult parse_interpolated_str(char* s_val, int32_t next_p) {
        if ((!stkt_str_contains(s_val, "{"))) {
        return (ParseResult){s_val, next_p};
    }
        int32_t n = ((int32_t)strlen(s_val));
        char* fmt_str = "";
        char* arg_str = "";
        bool has_arg = false;
        int32_t i = 0;
        while (i < n) {
        if (s_val[i] == '{') {
        int32_t j = i + 1;
        while (j < n && s_val[j] != '}') {
        j = j + 1;
    }
        if (j < n && s_val[j] == '}') {
        char* var_expr = stkt_str_slice(s_val, (i + 1), j);
        if (is_valid_interp_var(var_expr)) {
        fmt_str = stkt_format("%s%%s", fmt_str);
        if (has_arg) {
        arg_str = stkt_format("%s, %s", arg_str, var_expr);
    }
        if ((!has_arg)) {
        arg_str = var_expr;
        has_arg = true;
    }
        i = j + 1;
    }
        if ((!is_valid_interp_var(var_expr))) {
        fmt_str = stkt_format("%s{", fmt_str);
        i = i + 1;
    }
    }
        if (j >= n || s_val[j] != '}') {
        fmt_str = stkt_format("%s{", fmt_str);
        i = i + 1;
    }
    }
        if (i < n && s_val[i] != '{') {
        if (s_val[i] == '%') {
        fmt_str = stkt_format("%s%%%%", fmt_str);
        i = i + 1;
    }
        if (i < n && s_val[i] != '{' && s_val[i] != '%') {
        char* ch_str = stkt_str_slice(s_val, i, (i + 1));
        fmt_str = stkt_format("%s%s", fmt_str, ch_str);
        i = i + 1;
    }
    }
    }
        if ((!has_arg)) {
        return (ParseResult){s_val, next_p};
    }
        InterpolatedStrNode node = (InterpolatedStrNode){fmt_str, arg_str, next_p};
        return (ParseResult){gen_interpolate(node), next_p};
}

ParseResult parse_idx_atom(char* src, int32_t start) {
        Token tok = next_token(src, start);
        if (tok.kind == TokenKind_TokLParen) {
        ParseResult inside = parse_ternary(src, tok.next_pos);
        Token close_lp = next_token(src, inside.next_pos);
        return (ParseResult){stkt_format("(%s)", inside.text), close_lp.next_pos};
    }
        if (tok.kind == TokenKind_TokLen || (tok.kind == TokenKind_TokIdent && (strcmp(tok.text, "len") == 0))) {
        int32_t p_len = tok.next_pos;
        Token tok_lp = next_token(src, p_len);
        Token arg_tok = next_token(src, tok_lp.next_pos);
        Token rp_tok = next_token(src, arg_tok.next_pos);
        if (is_slice_var(src, arg_tok.text)) {
        return (ParseResult){stkt_format("STKT_SLICE_LEN(%s)", arg_tok.text), rp_tok.next_pos};
    }
        return (ParseResult){stkt_format("((int32_t)strlen(%s))", arg_tok.text), rp_tok.next_pos};
    }
        if (tok.kind == TokenKind_TokInt) {
        return (ParseResult){tok.text, tok.next_pos};
    }
        if (tok.kind == TokenKind_TokIdent) {
        int32_t p_id = tok.next_pos;
        Token tok_next = next_token(src, p_id);
        char* id_text = tok.text;
        bool is_range_dot = false;
        if (tok_next.kind == TokenKind_TokDot) {
        Token peek_dot2 = next_token(src, tok_next.next_pos);
        if (peek_dot2.kind == TokenKind_TokDot) {
        is_range_dot = true;
    }
    }
        while (tok_next.kind == TokenKind_TokDot && (!is_range_dot)) {
        Token field_tok = next_token(src, tok_next.next_pos);
        id_text = stkt_format("%s.%s", id_text, field_tok.text);
        p_id = field_tok.next_pos;
        tok_next = next_token(src, p_id);
        if (tok_next.kind == TokenKind_TokDot) {
        Token peek_dot3 = next_token(src, tok_next.next_pos);
        if (peek_dot3.kind == TokenKind_TokDot) {
        is_range_dot = true;
    }
    }
    }
        return (ParseResult){id_text, p_id};
    }
        return (ParseResult){tok.text, tok.next_pos};
}

ParseResult parse_idx_expr(char* src, int32_t start) {
        ParseResult res = parse_idx_atom(src, start);
        while (true) {
        Token op_tok = next_token(src, res.next_pos);
        if (op_tok.kind != TokenKind_TokPlus && op_tok.kind != TokenKind_TokMinus) {
        return res;
    }
        ParseResult rhs = parse_idx_atom(src, op_tok.next_pos);
        char* combined = stkt_format("%s %s %s", res.text, op_tok.text, rhs.text);
        res = (ParseResult){combined, rhs.next_pos};
    }
        return res;
}

ParseResult parse_primary(char* src, int32_t start) {
        int32_t p = start;
        Token tok_primary = next_token(src, p);
        if (tok_primary.kind == TokenKind_TokPop || (tok_primary.kind == TokenKind_TokIdent && (strcmp(tok_primary.text, "pop") == 0))) {
        p = tok_primary.next_pos;
        Token tok_lp_pop = next_token(src, p);
        p = tok_lp_pop.next_pos;
        Token tok_arr_pop = next_token(src, p);
        p = tok_arr_pop.next_pos;
        Token tok_rp_pop = next_token(src, p);
        p = tok_rp_pop.next_pos;
        return (ParseResult){stkt_format("STKT_SLICE_POP(%s)", tok_arr_pop.text), p};
    }
        if (tok_primary.kind == TokenKind_TokLen || (tok_primary.kind == TokenKind_TokIdent && (strcmp(tok_primary.text, "len") == 0))) {
        p = tok_primary.next_pos;
        Token tok_lp_len = next_token(src, p);
        p = tok_lp_len.next_pos;
        ParseResult len_arg_res = parse_primary(src, p);
        p = len_arg_res.next_pos;
        Token tok_rp_len = next_token(src, p);
        p = tok_rp_len.next_pos;
        if (is_slice_var(src, len_arg_res.text)) {
        return (ParseResult){stkt_format("STKT_SLICE_LEN(%s)", len_arg_res.text), p};
    }
        return (ParseResult){stkt_format("((int32_t)strlen(%s))", len_arg_res.text), p};
    }
        if (tok_primary.kind == TokenKind_TokStr) {
        return parse_interpolated_str(tok_primary.text, tok_primary.next_pos);
    }
        if (tok_primary.kind == TokenKind_TokInt || tok_primary.kind == TokenKind_TokFloat || tok_primary.kind == TokenKind_TokChar || tok_primary.kind == TokenKind_TokTrue || tok_primary.kind == TokenKind_TokFalse) {
        return (ParseResult){tok_primary.text, tok_primary.next_pos};
    }
        if (tok_primary.kind == TokenKind_TokNot || tok_primary.kind == TokenKind_TokMinus) {
        char* u_ops_str = tok_primary.text;
        p = tok_primary.next_pos;
        ParseResult u_operand = parse_primary(src, p);
        p = u_operand.next_pos;
        UnaryNode node_unary = (UnaryNode){u_operand.text, u_ops_str, p};
        return (ParseResult){gen_unary(node_unary), p};
    }
        if (tok_primary.kind == TokenKind_TokLambda) {
        p = tok_primary.next_pos;
        Token tok_colon1 = next_token(src, p);
        p = tok_colon1.next_pos;
        Token ret_type = next_token(src, p);
        p = ret_type.next_pos;
        Token tok_lp = next_token(src, p);
        p = tok_lp.next_pos;
        while (true) {
        Token tok_peek_lp = next_token(src, p);
        if (tok_peek_lp.kind == TokenKind_TokRParen || tok_peek_lp.kind == TokenKind_TokEof) {
        p = tok_peek_lp.next_pos;
        break;
    }
        p = tok_peek_lp.next_pos;
    }
        Token tok_lbrace_lambda = next_token(src, p);
        p = tok_lbrace_lambda.next_pos;
        while (true) {
        Token lambda_peek = next_token(src, p);
        if (lambda_peek.kind == TokenKind_TokRBrace || lambda_peek.kind == TokenKind_TokEof) {
        p = lambda_peek.next_pos;
        break;
    }
        p = lambda_peek.next_pos;
    }
        return (ParseResult){"__lambda_0", p};
    }
        if (tok_primary.kind == TokenKind_TokLBracket) {
        p = tok_primary.next_pos;
        char* elems_str = "";
        bool has_elem = false;
        Token tok_first_elem = next_token(src, p);
        if (tok_first_elem.kind != TokenKind_TokRBracket) {
        while (true) {
        ParseResult elem_res = parse_primary(src, p);
        p = elem_res.next_pos;
        if (has_elem) {
        elems_str = stkt_format("%s, %s", elems_str, elem_res.text);
    }
        if ((!has_elem)) {
        elems_str = elem_res.text;
        has_elem = true;
    }
        Token sep_elem = next_token(src, p);
        p = sep_elem.next_pos;
        if (sep_elem.kind == TokenKind_TokRBracket) {
        break;
    }
    }
    }
        if (tok_first_elem.kind == TokenKind_TokRBracket) {
        p = tok_first_elem.next_pos;
    }
        char* lit_str = stkt_format("{%s}", elems_str);
        return (ParseResult){lit_str, p};
    }
        if (tok_primary.kind == TokenKind_TokLParen) {
        p = tok_primary.next_pos;
        Token tok_inside = next_token(src, p);
        Token tok_after = next_token(src, tok_inside.next_pos);
        if (is_primitive_type(tok_inside.text) && tok_after.kind == TokenKind_TokRParen) {
        p = tok_after.next_pos;
        ParseResult cast_val = parse_primary(src, p);
        CastNode node_cast = (CastNode){tok_inside.text, cast_val.text, cast_val.next_pos};
        return (ParseResult){gen_cast(node_cast), cast_val.next_pos};
    }
        ParseResult grp_res = parse_ternary(src, p);
        char* grp_text = stkt_format("(%s)", grp_res.text);
        Token tok_close_grp = next_token(src, grp_res.next_pos);
        int32_t grp_p = tok_close_grp.next_pos;
        while (true) {
        Token peek_grp_err = next_token(src, grp_p);
        if (peek_grp_err.kind == TokenKind_TokDot) {
        Token tok_grp_mem = next_token(src, peek_grp_err.next_pos);
        if (tok_grp_mem.kind == TokenKind_TokIsok || (strcmp(tok_grp_mem.text, "isok?") == 0)) {
        Token tok_grp_isok_lp = next_token(src, tok_grp_mem.next_pos);
        ParseResult msg_grp_res = parse_primary(src, tok_grp_isok_lp.next_pos);
        Token tok_grp_isok_rp = next_token(src, msg_grp_res.next_pos);
        IsOkNode isok_grp_node = (IsOkNode){grp_text, msg_grp_res.text, "", 0};
        grp_text = gen_isok(isok_grp_node);
        grp_p = tok_grp_isok_rp.next_pos;
        continue;
    }
        if ((strcmp(tok_grp_mem.text, "or") == 0)) {
        Token tok_grp_or_lp = next_token(src, tok_grp_mem.next_pos);
        ParseResult fb_grp_res = parse_primary(src, tok_grp_or_lp.next_pos);
        Token tok_grp_or_rp = next_token(src, fb_grp_res.next_pos);
        OrNode or_grp_node = (OrNode){grp_text, fb_grp_res.text, "", 0};
        grp_text = gen_or(or_grp_node);
        grp_p = tok_grp_or_rp.next_pos;
        continue;
    }
    }
        break;
    }
        return (ParseResult){grp_text, grp_p};
    }
        if (tok_primary.kind == TokenKind_TokOnkey) {
        p = tok_primary.next_pos;
        Token tok_scan = next_token(src, p);
        p = tok_scan.next_pos;
        Token tok_type = next_token(src, p);
        p = tok_type.next_pos;
        ScanNode node_scan = (ScanNode){tok_type.text, p};
        return (ParseResult){gen_scan(node_scan), p};
    }
        if (tok_primary.kind == TokenKind_TokIdent) {
        p = tok_primary.next_pos;
        Token tok_peek = next_token(src, p);
        char* res_text = "";
        if (tok_peek.kind == TokenKind_TokLParen) {
        p = tok_peek.next_pos;
        char* args_str = "";
        bool has_arg = false;
        Token tok_arg_first = next_token(src, p);
        if (tok_arg_first.kind != TokenKind_TokRParen) {
        while (true) {
        ParseResult arg_res = parse_ternary(src, p);
        p = arg_res.next_pos;
        if (has_arg) {
        args_str = stkt_format("%s, %s", args_str, arg_res.text);
    }
        if ((!has_arg)) {
        args_str = arg_res.text;
        has_arg = true;
    }
        Token sep_arg = next_token(src, p);
        p = sep_arg.next_pos;
        if (sep_arg.kind == TokenKind_TokRParen) {
        break;
    }
    }
    }
        if (tok_arg_first.kind == TokenKind_TokRParen) {
        p = tok_arg_first.next_pos;
    }
        if (is_struct_name(src, tok_primary.text)) {
        char* l_b = "{";
        char* r_b = "}";
        res_text = stkt_format("(%s)%s%s%s", tok_primary.text, l_b, args_str, r_b);
    }
        if ((!is_struct_name(src, tok_primary.text))) {
        res_text = stkt_format("%s(%s)", tok_primary.text, args_str);
    }
    }
        if (tok_peek.kind == TokenKind_TokLBracket) {
        p = tok_peek.next_pos;
        ParseResult idx_res = parse_idx_expr(src, p);
        p = idx_res.next_pos;
        Token tok_close = next_token(src, p);
        if (tok_close.kind == TokenKind_TokDot) {
        Token tok_dot2 = next_token(src, tok_close.next_pos);
        if (tok_dot2.kind == TokenKind_TokDot) {
        p = tok_dot2.next_pos;
        ParseResult end_res = parse_idx_expr(src, p);
        p = end_res.next_pos;
        Token tok_rb = next_token(src, p);
        p = tok_rb.next_pos;
        res_text = stkt_format("stkt_str_slice(%s, %s, %s)", tok_primary.text, idx_res.text, end_res.text);
    }
    }
        if (tok_close.kind != TokenKind_TokDot) {
        p = tok_close.next_pos;
        if (is_slice_var(src, tok_primary.text)) {
        res_text = stkt_format("%s.buf->data[%s]", tok_primary.text, idx_res.text);
    }
        if ((!is_slice_var(src, tok_primary.text))) {
        IndexAccessNode node_access = (IndexAccessNode){tok_primary.text, idx_res.text, p};
        res_text = gen_index_access(node_access);
    }
    }
    }
        if (tok_peek.kind == TokenKind_TokDot) {
        p = tok_peek.next_pos;
        Token member_tok = next_token(src, p);
        p = member_tok.next_pos;
        Token after_member = next_token(src, p);
        if (after_member.kind == TokenKind_TokLParen) {
        p = after_member.next_pos;
        char* dot_args = "";
        bool dot_has_args = false;
        Token tok_first_arg = next_token(src, p);
        if (tok_first_arg.kind != TokenKind_TokRParen) {
        while (true) {
        ParseResult dot_arg_res = parse_ternary(src, p);
        p = dot_arg_res.next_pos;
        if (dot_has_args) {
        dot_args = stkt_format("%s, %s", dot_args, dot_arg_res.text);
    }
        if ((!dot_has_args)) {
        dot_args = dot_arg_res.text;
        dot_has_args = true;
    }
        Token dot_sep = next_token(src, p);
        p = dot_sep.next_pos;
        if (dot_sep.kind == TokenKind_TokRParen) {
        break;
    }
    }
    }
        if (tok_first_arg.kind == TokenKind_TokRParen) {
        p = tok_first_arg.next_pos;
    }
        char* target_name = tok_primary.text;
        char* member_name = member_tok.text;
        if (is_module_name(src, target_name)) {
        if ((strcmp(target_name, "math") == 0) && ((strcmp(member_name, "sqrt") == 0) || (strcmp(member_name, "pow") == 0) || (strcmp(member_name, "floor") == 0) || (strcmp(member_name, "ceil") == 0) || (strcmp(member_name, "sin") == 0) || (strcmp(member_name, "cos") == 0))) {
        res_text = stkt_format("%s(%s)", member_name, dot_args);
    }
        if ((strcmp(target_name, "math") != 0) || ((strcmp(member_name, "sqrt") != 0) && (strcmp(member_name, "pow") != 0) && (strcmp(member_name, "floor") != 0) && (strcmp(member_name, "ceil") != 0) && (strcmp(member_name, "sin") != 0) && (strcmp(member_name, "cos") != 0))) {
        res_text = stkt_format("%s_%s(%s)", target_name, member_name, dot_args);
    }
    }
        if ((!is_module_name(src, target_name)) && is_hmap_var(src, target_name)) {
        bool is_str_map = is_hmap_str_str(src, target_name);
        if ((strcmp(member_name, "set") == 0)) {
        if (is_str_map) {
        res_text = stkt_format("__stkt_map_set_str_str(%s, %s)", target_name, dot_args);
    }
        if ((!is_str_map)) {
        res_text = stkt_format("__stkt_map_set_str_i32(%s, %s)", target_name, dot_args);
    }
    }
        if ((strcmp(member_name, "has") == 0)) {
        if (is_str_map) {
        res_text = stkt_format("__stkt_map_has_str_str(%s, %s)", target_name, dot_args);
    }
        if ((!is_str_map)) {
        res_text = stkt_format("__stkt_map_has_str_i32(%s, %s)", target_name, dot_args);
    }
    }
        if ((strcmp(member_name, "keys") == 0)) {
        if (is_str_map) {
        res_text = stkt_format("__stkt_map_keys_str_str(%s)", target_name);
    }
        if ((!is_str_map)) {
        res_text = stkt_format("__stkt_map_keys_str_i32(%s)", target_name);
    }
    }
        if ((strcmp(member_name, "get") == 0)) {
        if (is_str_map) {
        res_text = stkt_format("__stkt_map_get_str_str(%s, %s)", target_name, dot_args);
    }
        if ((!is_str_map)) {
        res_text = stkt_format("__stkt_map_get_str_i32(%s, %s)", target_name, dot_args);
    }
    }
    }
        if ((!is_module_name(src, target_name)) && (!is_hmap_var(src, target_name))) {
        if ((strcmp(member_name, "trim") == 0)) {
        res_text = stkt_format("stkt_str_trim(%s)", target_name);
    }
        if ((strcmp(member_name, "split") == 0)) {
        res_text = stkt_format("stkt_str_split(%s, %s)", target_name, dot_args);
    }
        if ((strcmp(member_name, "contains") == 0)) {
        res_text = stkt_format("stkt_str_contains(%s, %s)", target_name, dot_args);
    }
        if ((strcmp(member_name, "trim") != 0) && (strcmp(member_name, "split") != 0) && (strcmp(member_name, "contains") != 0)) {
        if (dot_has_args) {
        dot_args = stkt_format("%s, %s", target_name, dot_args);
    }
        if ((!dot_has_args)) {
        dot_args = target_name;
    }
        res_text = stkt_format("%s(%s)", member_name, dot_args);
    }
    }
    }
        if (after_member.kind != TokenKind_TokLParen) {
        TypeAccessNode node_acc = (TypeAccessNode){tok_primary.text, member_tok.text, p};
        res_text = gen_typeaccess(src, node_acc);
    }
    }
        if (tok_peek.kind != TokenKind_TokLParen && tok_peek.kind != TokenKind_TokLBracket && tok_peek.kind != TokenKind_TokDot) {
        res_text = tok_primary.text;
    }
        while (true) {
        Token peek_id_err = next_token(src, p);
        if (peek_id_err.kind == TokenKind_TokDot) {
        Token tok_id_mem = next_token(src, peek_id_err.next_pos);
        if (tok_id_mem.kind == TokenKind_TokIsok || (strcmp(tok_id_mem.text, "isok?") == 0)) {
        Token tok_id_isok_lp = next_token(src, tok_id_mem.next_pos);
        ParseResult msg_id_res = parse_primary(src, tok_id_isok_lp.next_pos);
        Token tok_id_isok_rp = next_token(src, msg_id_res.next_pos);
        IsOkNode isok_id_node = (IsOkNode){res_text, msg_id_res.text, "", 0};
        res_text = gen_isok(isok_id_node);
        p = tok_id_isok_rp.next_pos;
        continue;
    }
        if ((strcmp(tok_id_mem.text, "or") == 0)) {
        Token tok_id_or_lp = next_token(src, tok_id_mem.next_pos);
        ParseResult fb_id_res = parse_primary(src, tok_id_or_lp.next_pos);
        Token tok_id_or_rp = next_token(src, fb_id_res.next_pos);
        OrNode or_id_node = (OrNode){res_text, fb_id_res.text, "", 0};
        res_text = gen_or(or_id_node);
        p = tok_id_or_rp.next_pos;
        continue;
    }
    }
        break;
    }
        return (ParseResult){res_text, p};
    }
        return (ParseResult){"", p};
}

ParseResult parse_term(char* src, int32_t start) {
        ParseResult res = parse_primary(src, start);
        while (true) {
        Token op_tok = next_token(src, res.next_pos);
        if (op_tok.kind != TokenKind_TokStar && op_tok.kind != TokenKind_TokSlash) {
        return res;
    }
        ParseResult rhs = parse_primary(src, op_tok.next_pos);
        char* combined = stkt_format("%s %s %s", res.text, op_tok.text, rhs.text);
        res = (ParseResult){combined, rhs.next_pos};
    }
        return res;
}

bool is_str_operand(char* src, char* expr) {
        if (((int32_t)strlen(expr)) >= 2 && expr[0] == '"') {
        return true;
    }
        if (stkt_str_contains(expr, ".text") || stkt_str_contains(expr, "stkt_str_") || stkt_str_contains(expr, "stkt_format(") || stkt_str_contains(expr, "read_text(") || stkt_str_contains(expr, "to_c_type(")) {
        return true;
    }
        char* t = find_var_type(src, expr);
        if ((strcmp(t, "str") == 0)) {
        return true;
    }
        return false;
}

ParseResult parse_additive(char* src, int32_t start) {
        ParseResult res = parse_term(src, start);
        while (true) {
        Token op_tok = next_token(src, res.next_pos);
        if (op_tok.kind != TokenKind_TokPlus && op_tok.kind != TokenKind_TokMinus) {
        return res;
    }
        ParseResult rhs = parse_term(src, op_tok.next_pos);
        bool is_s = is_str_operand(src, res.text) || is_str_operand(src, rhs.text);
        char* combined = "";
        if (is_s && op_tok.kind == TokenKind_TokPlus) {
        combined = stkt_format("stkt_str_concat(%s, %s)", res.text, rhs.text);
    }
        if ((!is_s) || op_tok.kind != TokenKind_TokPlus) {
        combined = stkt_format("%s %s %s", res.text, op_tok.text, rhs.text);
    }
        res = (ParseResult){combined, rhs.next_pos};
    }
        return res;
}

ParseResult parse_relational(char* src, int32_t start) {
        ParseResult res = parse_additive(src, start);
        while (true) {
        Token op_tok = next_token(src, res.next_pos);
        if (op_tok.kind != TokenKind_TokGt && op_tok.kind != TokenKind_TokLt && op_tok.kind != TokenKind_TokGe && op_tok.kind != TokenKind_TokLe) {
        return res;
    }
        ParseResult rhs = parse_additive(src, op_tok.next_pos);
        char* combined = stkt_format("%s %s %s", res.text, op_tok.text, rhs.text);
        res = (ParseResult){combined, rhs.next_pos};
    }
        return res;
}

ParseResult parse_equality(char* src, int32_t start) {
        ParseResult res = parse_relational(src, start);
        while (true) {
        Token op_tok = next_token(src, res.next_pos);
        if (op_tok.kind != TokenKind_TokEq && op_tok.kind != TokenKind_TokNe) {
        return res;
    }
        ParseResult rhs = parse_relational(src, op_tok.next_pos);
        bool is_s = is_str_operand(src, res.text) || is_str_operand(src, rhs.text);
        char* combined = "";
        if (is_s && op_tok.kind == TokenKind_TokEq) {
        combined = stkt_format("(strcmp(%s, %s) == 0)", res.text, rhs.text);
    }
        if (is_s && op_tok.kind == TokenKind_TokNe) {
        combined = stkt_format("(strcmp(%s, %s) != 0)", res.text, rhs.text);
    }
        if ((!is_s)) {
        combined = stkt_format("%s %s %s", res.text, op_tok.text, rhs.text);
    }
        res = (ParseResult){combined, rhs.next_pos};
    }
        return res;
}

ParseResult parse_logical_and(char* src, int32_t start) {
        ParseResult res = parse_equality(src, start);
        while (true) {
        Token op_tok = next_token(src, res.next_pos);
        if (op_tok.kind != TokenKind_TokAnd) {
        return res;
    }
        ParseResult rhs = parse_equality(src, op_tok.next_pos);
        char* combined = stkt_format("%s && %s", res.text, rhs.text);
        res = (ParseResult){combined, rhs.next_pos};
    }
        return res;
}

ParseResult parse_expr(char* src, int32_t start) {
        ParseResult res = parse_logical_and(src, start);
        while (true) {
        Token op_tok = next_token(src, res.next_pos);
        if (op_tok.kind != TokenKind_TokOr) {
        return res;
    }
        ParseResult rhs = parse_logical_and(src, op_tok.next_pos);
        char* combined = stkt_format("%s || %s", res.text, rhs.text);
        res = (ParseResult){combined, rhs.next_pos};
    }
        return res;
}

ParseResult parse_ternary(char* src, int32_t start) {
        int32_t p = start;
        ParseResult cond = parse_expr(src, p);
        p = cond.next_pos;
        Token tok_ternary = next_token(src, p);
        if (tok_ternary.kind != TokenKind_TokQuestion) {
        return cond;
    }
        p = tok_ternary.next_pos;
        ParseResult true_res = parse_expr(src, p);
        p = true_res.next_pos;
        char* true_str = true_res.text;
        Token tok_colon = next_token(src, p);
        p = tok_colon.next_pos;
        ParseResult false_res = parse_expr(src, p);
        p = false_res.next_pos;
        char* false_str = false_res.text;
        TernaryNode n_ternary = (TernaryNode){cond.text, true_str, false_str, p};
        return (ParseResult){gen_ternary(n_ternary), p};
}

LetNode parse_let(char* src, int32_t start) {
        int32_t p = start;
        Token tok_let = next_token(src, p);
        p = tok_let.next_pos;
        Token tok_ident = next_token(src, p);
        p = tok_ident.next_pos;
        Token tok_next = next_token(src, p);
        p = tok_next.next_pos;
        char* type_name = "i32";
        if (tok_next.kind == TokenKind_TokColon) {
        Token tok_t = next_token(src, p);
        p = tok_t.next_pos;
        type_name = tok_t.text;
        if (tok_t.kind == TokenKind_TokLBracket) {
        Token tok_elem = next_token(src, p);
        p = tok_elem.next_pos;
        Token tok_rb = next_token(src, p);
        p = tok_rb.next_pos;
        type_name = stkt_format("[%s]", tok_elem.text);
    }
        if ((strcmp(tok_t.text, "hmap") == 0)) {
        p = tok_t.next_pos;
        Token tok_lb_m = next_token(src, p);
        p = tok_lb_m.next_pos;
        Token tok_k_t = next_token(src, p);
        p = tok_k_t.next_pos;
        Token tok_sep_m = next_token(src, p);
        p = tok_sep_m.next_pos;
        Token tok_v_t = next_token(src, p);
        p = tok_v_t.next_pos;
        Token tok_rb_m = next_token(src, p);
        p = tok_rb_m.next_pos;
        Token tok_eq_m = next_token(src, p);
        p = tok_eq_m.next_pos;
        Token tok_val_m = next_token(src, p);
        p = tok_val_m.next_pos;
        if (tok_val_m.kind == TokenKind_TokLBrace) {
        Token tok_peek_rb = next_token(src, p);
        if (tok_peek_rb.kind == TokenKind_TokRBrace) {
        p = tok_peek_rb.next_pos;
    }
    }
        if ((strcmp(tok_val_m.text, "hmap") == 0) || tok_val_m.kind == TokenKind_TokHMap) {
        Token tok_lp_m = next_token(src, p);
        if (tok_lp_m.kind == TokenKind_TokLParen) {
        p = tok_lp_m.next_pos;
        Token tok_rp_m = next_token(src, p);
        if (tok_rp_m.kind == TokenKind_TokRParen) {
        p = tok_rp_m.next_pos;
    }
    }
    }
        char* map_init_val = "__stkt_map_create_str_i32()";
        char* map_c_type = "__stkt_map_str_i32*";
        if ((strcmp(tok_v_t.text, "str") == 0)) {
        map_init_val = "__stkt_map_create_str_str()";
        map_c_type = "__stkt_map_str_str*";
    }
        return (LetNode){tok_ident.text, map_c_type, map_init_val, p};
    }
        Token tok_peek = next_token(src, p);
        if (tok_peek.kind == TokenKind_TokLBracket) {
        p = tok_peek.next_pos;
        Token tok_num = next_token(src, p);
        p = tok_num.next_pos;
        Token tok_close = next_token(src, p);
        p = tok_close.next_pos;
        int32_t cap = tok_num.val;
        type_name = stkt_format("%s[%s]", tok_t.text, cap);
    }
        Token tok_eq = next_token(src, p);
        p = tok_eq.next_pos;
    }
        ParseResult expr_res = parse_ternary(src, p);
        p = expr_res.next_pos;
        char* str_val = expr_res.text;
        if (tok_next.kind != TokenKind_TokColon) {
        if (((int32_t)strlen(str_val)) > 0 && (strcmp(stkt_str_slice(str_val, 0, 1), "\"") == 0)) {
        type_name = "str";
    }
        if (((int32_t)strlen(str_val)) > 0 && (strcmp(stkt_str_slice(str_val, 0, 1), "'") == 0)) {
        type_name = "char";
    }
        if ((strcmp(str_val, "true") == 0) || (strcmp(str_val, "false") == 0)) {
        type_name = "bool";
    }
    }
        return (LetNode){tok_ident.text, type_name, str_val, p};
}

ArrayDeclNode parse_array_decl(char* src, int32_t start) {
        int32_t p = start;
        Token tok_let = next_token(src, p);
        p = tok_let.next_pos;
        Token tok_name = next_token(src, p);
        p = tok_name.next_pos;
        Token tok_lbracket = next_token(src, p);
        p = tok_lbracket.next_pos;
        Token tok_size = next_token(src, p);
        p = tok_size.next_pos;
        char* size_val = tok_size.text;
        Token tok_rbracket = next_token(src, p);
        p = tok_rbracket.next_pos;
        Token tok_colon = next_token(src, p);
        p = tok_colon.next_pos;
        Token tok_type = next_token(src, p);
        p = tok_type.next_pos;
        char* type_name = tok_type.text;
        char* elems_str = "";
        Token tok_peek = next_token(src, p);
        if (tok_peek.kind == TokenKind_TokAssign) {
        p = tok_peek.next_pos;
        ParseResult elems_res = parse_primary(src, p);
        p = elems_res.next_pos;
        elems_str = elems_res.text;
    }
        return (ArrayDeclNode){tok_name.text, size_val, type_name, elems_str, p};
}

AssignNode parse_assign(char* src, int32_t start) {
        int32_t p = start;
        Token tok_ident = next_token(src, p);
        p = tok_ident.next_pos;
        Token tok_assign = next_token(src, p);
        p = tok_assign.next_pos;
        ParseResult val_res = parse_ternary(src, p);
        p = val_res.next_pos;
        return (AssignNode){tok_ident.text, val_res.text, p};
}

IndexAssignNode parse_index_assign(char* src, int32_t start) {
        int32_t p = start;
        Token tok_name = next_token(src, p);
        p = tok_name.next_pos;
        Token tok_lbracket = next_token(src, p);
        p = tok_lbracket.next_pos;
        ParseResult idx_res = parse_primary(src, p);
        p = idx_res.next_pos;
        Token tok_rbracket = next_token(src, p);
        p = tok_rbracket.next_pos;
        Token tok_eq = next_token(src, p);
        p = tok_eq.next_pos;
        ParseResult val_res = parse_ternary(src, p);
        p = val_res.next_pos;
        return (IndexAssignNode){tok_name.text, idx_res.text, val_res.text, p};
}

CallNode parse_call(char* src, int32_t start) {
        int32_t p = start;
        Token tok_name = next_token(src, p);
        p = tok_name.next_pos;
        Token tok_lparen = next_token(src, p);
        p = tok_lparen.next_pos;
        char* args_str = "";
        bool has_arg = false;
        Token tok_first = next_token(src, p);
        if (tok_first.kind != TokenKind_TokRParen) {
        while (true) {
        ParseResult arg_res = parse_ternary(src, p);
        p = arg_res.next_pos;
        if (has_arg) {
        args_str = stkt_format("%s, %s", args_str, arg_res.text);
    }
        if ((!has_arg)) {
        args_str = arg_res.text;
        has_arg = true;
    }
        Token sep = next_token(src, p);
        p = sep.next_pos;
        if (sep.kind == TokenKind_TokRParen) {
        break;
    }
    }
    }
        if (tok_first.kind == TokenKind_TokRParen) {
        p = tok_first.next_pos;
    }
        return (CallNode){tok_name.text, args_str, p};
}

PrintNode parse_onscreen(char* src, int32_t start) {
        int32_t p = start;
        Token tok_os = next_token(src, p);
        p = tok_os.next_pos;
        ParseResult val_res = parse_expr(src, p);
        p = val_res.next_pos;
        char* type_name = find_var_type(src, val_res.text);
        return (PrintNode){val_res.text, type_name, p};
}

ReturnNode parse_return(char* src, int32_t start) {
        int32_t p = start;
        Token tok_ret = next_token(src, p);
        p = tok_ret.next_pos;
        ParseResult expr_res = parse_ternary(src, p);
        p = expr_res.next_pos;
        return (ReturnNode){expr_res.text, p};
}

BreakNode parse_break(char* src, int32_t start) {
        int32_t p = start;
        Token tok_break = next_token(src, p);
        p = tok_break.next_pos;
        return (BreakNode){p};
}

ContinueNode parse_continue(char* src, int32_t start) {
        int32_t p = start;
        Token tok_cont = next_token(src, p);
        p = tok_cont.next_pos;
        return (ContinueNode){p};
}

ConstNode parse_const(char* src, int32_t start) {
        int32_t p = start;
        Token tok_const = next_token(src, p);
        p = tok_const.next_pos;
        Token tok_name = next_token(src, p);
        p = tok_name.next_pos;
        char* name_str = tok_name.text;
        Token tok_colon = next_token(src, p);
        p = tok_colon.next_pos;
        Token tok_type = next_token(src, p);
        p = tok_type.next_pos;
        char* c_type = to_c_type(tok_type.text);
        Token tok_assign = next_token(src, p);
        p = tok_assign.next_pos;
        ParseResult val_res = parse_ternary(src, p);
        p = val_res.next_pos;
        return (ConstNode){name_str, c_type, val_res.text, p};
}

ParseResult collect_until_semi(char* src, int32_t start) {
        int32_t p = start;
        char* text = "";
        bool has_text = false;
        while (true) {
        Token tok = next_token(src, p);
        if (tok.kind == TokenKind_TokSemicolon || tok.kind == TokenKind_TokEof) {
        p = tok.next_pos;
        break;
    }
        if (has_text) {
        text = stkt_format("%s %s", text, tok.text);
    }
        if ((!has_text)) {
        text = tok.text;
        has_text = true;
    }
        p = tok.next_pos;
    }
        return (ParseResult){text, p};
}

ParseResult collect_until_brace(char* src, int32_t start) {
        int32_t p = start;
        char* text = "";
        bool has_text = false;
        while (true) {
        Token tok = next_token(src, p);
        if (tok.kind == TokenKind_TokLBrace || tok.kind == TokenKind_TokRParen || tok.kind == TokenKind_TokEof) {
        break;
    }
        if (has_text) {
        text = stkt_format("%s %s", text, tok.text);
    }
        if ((!has_text)) {
        text = tok.text;
        has_text = true;
    }
        p = tok.next_pos;
    }
        return (ParseResult){text, p};
}

FieldNode parse_field(char* src, int32_t start) {
        int32_t p = start;
        Token tok_field_ident = next_token(src, p);
        p = tok_field_ident.next_pos;
        char* field_ident = tok_field_ident.text;
        Token tok_colon = next_token(src, p);
        p = tok_colon.next_pos;
        Token type_token = next_token(src, p);
        p = type_token.next_pos;
        char* type_str = type_token.text;
        char* c_type_str = to_c_type(type_str);
        Token tok_sep = next_token(src, p);
        if (tok_sep.kind == TokenKind_TokComma) {
        p = tok_sep.next_pos;
    }
        return (FieldNode){field_ident, c_type_str, p};
}

TypeDeclNode parse_typedecl(char* src, int32_t start) {
        int32_t p = start;
        Token tok_type_kw = next_token(src, p);
        p = tok_type_kw.next_pos;
        Token tok_ident = next_token(src, p);
        p = tok_ident.next_pos;
        char* struct_ident = tok_ident.text;
        Token tok_brace1 = next_token(src, p);
        p = tok_brace1.next_pos;
        char* field_str = "";
        while (true) {
        Token peek = next_token(src, p);
        if (peek.kind == TokenKind_TokRBrace || peek.kind == TokenKind_TokEof) {
        p = peek.next_pos;
        break;
    }
        FieldNode field_node = parse_field(src, p);
        p = field_node.next;
        char* field_code = gen_field(field_node);
        field_str = stkt_format("%s%s\n", field_str, field_code);
    }
        return (TypeDeclNode){struct_ident, field_str, p};
}

EnumNode parse_enum(char* src, int32_t start) {
        int32_t p = start;
        Token tok_enum_kw = next_token(src, p);
        p = tok_enum_kw.next_pos;
        Token tok_enum_ident = next_token(src, p);
        p = tok_enum_ident.next_pos;
        char* enum_ident = tok_enum_ident.text;
        Token tok_enum_lbrace = next_token(src, p);
        p = tok_enum_lbrace.next_pos;
        char* variant_str = "";
        while (true) {
        Token tok_peek = next_token(src, p);
        if (tok_peek.kind == TokenKind_TokRBrace || tok_peek.kind == TokenKind_TokEof) {
        p = tok_peek.next_pos;
        break;
    }
        Token var_tok = next_token(src, p);
        p = var_tok.next_pos;
        Token sep = next_token(src, p);
        if (sep.kind == TokenKind_TokComma) {
        p = sep.next_pos;
    }
        variant_str = stkt_format("%s    %s_%s,\n", variant_str, enum_ident, var_tok.text);
    }
        return (EnumNode){enum_ident, variant_str, p};
}

SliceDeclNode parse_slice_decl(char* src, int32_t start) {
        int32_t p = start;
        Token tok_let = next_token(src, p);
        p = tok_let.next_pos;
        Token tok_name = next_token(src, p);
        p = tok_name.next_pos;
        Token tok_colon = next_token(src, p);
        p = tok_colon.next_pos;
        Token tok_lbracket = next_token(src, p);
        p = tok_lbracket.next_pos;
        Token tok_elem_type = next_token(src, p);
        p = tok_elem_type.next_pos;
        char* elem_type_name = tok_elem_type.text;
        Token tok_rbracket = next_token(src, p);
        p = tok_rbracket.next_pos;
        Token tok_eq = next_token(src, p);
        p = tok_eq.next_pos;
        ParseResult elems_res = parse_primary(src, p);
        p = elems_res.next_pos;
        return (SliceDeclNode){tok_name.text, elem_type_name, elems_res.text, p};
}

StmtResult parse_stmt(char* src, int32_t start) {
        Token tok = next_token(src, start);
        int32_t p = start;
        if (tok.kind == TokenKind_TokLet) {
        int32_t p_peek = tok.next_pos;
        Token tok_name = next_token(src, p_peek);
        Token tok_after_name = next_token(src, tok_name.next_pos);
        if (tok_after_name.kind == TokenKind_TokLBracket) {
        ArrayDeclNode n_arr = parse_array_decl(src, start);
        return (StmtResult){gen_array_decl(n_arr), n_arr.next};
    }
        if (tok_after_name.kind == TokenKind_TokColon) {
        Token tok_after_colon = next_token(src, tok_after_name.next_pos);
        if (tok_after_colon.kind == TokenKind_TokLBracket) {
        int32_t p_chk = tok_after_colon.next_pos;
        Token tok_elem_chk = next_token(src, p_chk);
        p_chk = tok_elem_chk.next_pos;
        Token tok_rb_chk = next_token(src, p_chk);
        p_chk = tok_rb_chk.next_pos;
        Token tok_eq_chk = next_token(src, p_chk);
        p_chk = tok_eq_chk.next_pos;
        Token tok_val_chk = next_token(src, p_chk);
        if (tok_val_chk.kind == TokenKind_TokLBracket) {
        SliceDeclNode n_slice = parse_slice_decl(src, start);
        return (StmtResult){gen_slice_decl(n_slice), n_slice.next};
    }
    }
    }
        LetNode n_let = parse_let(src, start);
        return (StmtResult){gen_let(n_let), n_let.next};
    }
        if (tok.kind == TokenKind_TokAppend || (tok.kind == TokenKind_TokIdent && (strcmp(tok.text, "append") == 0))) {
        int32_t p_app = tok.next_pos;
        Token tok_lp = next_token(src, p_app);
        p_app = tok_lp.next_pos;
        Token tok_arr = next_token(src, p_app);
        p_app = tok_arr.next_pos;
        Token tok_comma = next_token(src, p_app);
        p_app = tok_comma.next_pos;
        ParseResult val_app_res = parse_ternary(src, p_app);
        p_app = val_app_res.next_pos;
        Token tok_rp = next_token(src, p_app);
        p_app = tok_rp.next_pos;
        AppendNode n_app = (AppendNode){tok_arr.text, val_app_res.text, p_app};
        return (StmtResult){gen_append(n_app), p_app};
    }
        if (tok.kind == TokenKind_TokIdent) {
        int32_t p_after = tok.next_pos;
        Token tok_ident_peek = next_token(src, p_after);
        if (tok_ident_peek.kind == TokenKind_TokLBracket) {
        IndexAssignNode n_idx = parse_index_assign(src, start);
        return (StmtResult){gen_index_assign_slice(src, n_idx), n_idx.next};
    }
        if (tok_ident_peek.kind == TokenKind_TokLParen) {
        CallNode n_call = parse_call(src, start);
        return (StmtResult){gen_call(n_call), n_call.next};
    }
        if (tok_ident_peek.kind == TokenKind_TokDot) {
        int32_t p_dot = tok_ident_peek.next_pos;
        Token member_tok = next_token(src, p_dot);
        int32_t p_member = member_tok.next_pos;
        Token tok_after_mem = next_token(src, p_member);
        if (tok_after_mem.kind == TokenKind_TokAssign) {
        int32_t p_val = tok_after_mem.next_pos;
        ParseResult dot_val_res = parse_ternary(src, p_val);
        char* code_assign = stkt_format("    %s.%s = %s;", tok.text, member_tok.text, dot_val_res.text);
        return (StmtResult){code_assign, dot_val_res.next_pos};
    }
        if (tok_after_mem.kind == TokenKind_TokLParen) {
        ParseResult call_primary = parse_primary(src, start);
        char* code_call = stkt_format("    %s;", call_primary.text);
        return (StmtResult){code_call, call_primary.next_pos};
    }
    }
        AssignNode n_assign = parse_assign(src, start);
        return (StmtResult){gen_assign(n_assign), n_assign.next};
    }
        if (tok.kind == TokenKind_TokOnscreen) {
        PrintNode n_print = parse_onscreen(src, start);
        return (StmtResult){gen_print(n_print), n_print.next};
    }
        if (tok.kind == TokenKind_TokReturn) {
        ReturnNode n_ret = parse_return(src, start);
        return (StmtResult){gen_return(n_ret), n_ret.next};
    }
        if (tok.kind == TokenKind_TokBreak) {
        BreakNode n_break = parse_break(src, start);
        return (StmtResult){gen_break(n_break), n_break.next};
    }
        if (tok.kind == TokenKind_TokContinue) {
        ContinueNode n_continue = parse_continue(src, start);
        return (StmtResult){gen_continue(n_continue), n_continue.next};
    }
        if (tok.kind == TokenKind_TokConst) {
        ConstNode n_const = parse_const(src, start);
        return (StmtResult){gen_const(n_const), n_const.next};
    }
        if (tok.kind == TokenKind_TokType) {
        TypeDeclNode n_type = parse_typedecl(src, start);
        return (StmtResult){gen_typedecl(n_type), n_type.next};
    }
        if (tok.kind == TokenKind_TokEnum) {
        EnumNode n_enum = parse_enum(src, start);
        return (StmtResult){gen_enum(n_enum), n_enum.next};
    }
        if (tok.kind == TokenKind_TokWhile) {
        p = tok.next_pos;
        ParseResult con_res = parse_expr(src, p);
        p = con_res.next_pos;
        Token tok_while_lbrace = next_token(src, p);
        p = tok_while_lbrace.next_pos;
        char* while_body = "";
        while (true) {
        Token tok_while_peek = next_token(src, p);
        if (tok_while_peek.kind == TokenKind_TokRBrace || tok_while_peek.kind == TokenKind_TokEof) {
        p = tok_while_peek.next_pos;
        break;
    }
        StmtResult stmt = parse_stmt(src, p);
        if (stmt.next_pos <= p) {
        break;
    }
        p = stmt.next_pos;
        while_body = stkt_format("%s    %s\n", while_body, stmt.code);
    }
        WhileNode n_while = (WhileNode){con_res.text, while_body, p};
        return (StmtResult){gen_while(n_while), p};
    }
        if (tok.kind == TokenKind_TokIf) {
        p = tok.next_pos;
        ParseResult cond_res = parse_expr(src, p);
        p = cond_res.next_pos;
        Token tok_if_lbrace = next_token(src, p);
        p = tok_if_lbrace.next_pos;
        char* if_body = "";
        while (true) {
        Token tok_if_peek = next_token(src, p);
        if (tok_if_peek.kind == TokenKind_TokRBrace || tok_if_peek.kind == TokenKind_TokEof) {
        p = tok_if_peek.next_pos;
        break;
    }
        StmtResult stmt2 = parse_stmt(src, p);
        if (stmt2.next_pos <= p) {
        break;
    }
        p = stmt2.next_pos;
        if_body = stkt_format("%s    %s\n", if_body, stmt2.code);
    }
        char* else_body = "";
        Token tok_else = next_token(src, p);
        if (tok_else.kind == TokenKind_TokElse) {
        p = tok_else.next_pos;
        Token peek_after_else = next_token(src, p);
        if (peek_after_else.kind == TokenKind_TokIf) {
        StmtResult stmt_elif = parse_stmt(src, p);
        p = stmt_elif.next_pos;
        else_body = stkt_format("    %s\n", stmt_elif.code);
    }
        if (peek_after_else.kind != TokenKind_TokIf) {
        Token tok_else_lbrace = peek_after_else;
        p = tok_else_lbrace.next_pos;
        while (true) {
        Token tok_else_peek = next_token(src, p);
        if (tok_else_peek.kind == TokenKind_TokRBrace || tok_else_peek.kind == TokenKind_TokEof) {
        p = tok_else_peek.next_pos;
        break;
    }
        StmtResult stmt3 = parse_stmt(src, p);
        if (stmt3.next_pos <= p) {
        break;
    }
        p = stmt3.next_pos;
        else_body = stkt_format("%s    %s\n", else_body, stmt3.code);
    }
    }
    }
        IfNode n_if = (IfNode){cond_res.text, if_body, else_body, p};
        return (StmtResult){gen_if(n_if), p};
    }
        if (tok.kind == TokenKind_TokFor) {
        p = tok.next_pos;
        Token tok_first = next_token(src, p);
        Token tok_second = next_token(src, tok_first.next_pos);
        if (tok_first.kind == TokenKind_TokIdent && tok_second.kind == TokenKind_TokIn) {
        char* ident_name = tok_first.text;
        p = tok_second.next_pos;
        ParseResult col = parse_expr(src, p);
        p = col.next_pos;
        char* col_str = col.text;
        Token tok_lbrace_forin = next_token(src, p);
        p = tok_lbrace_forin.next_pos;
        char* body_str = "";
        while (true) {
        Token tok_peek_forin = next_token(src, p);
        if (tok_peek_forin.kind == TokenKind_TokRBrace || tok_peek_forin.kind == TokenKind_TokEof) {
        p = tok_peek_forin.next_pos;
        break;
    }
        StmtResult stmt_forin = parse_stmt(src, p);
        if (stmt_forin.next_pos <= p) {
        break;
    }
        p = stmt_forin.next_pos;
        body_str = stkt_format("%s    %s\n", body_str, stmt_forin.code);
    }
        ForinNode n_forin = (ForinNode){ident_name, col_str, body_str, p};
        return (StmtResult){gen_for_in(n_forin), p};
    }
        if (tok_first.kind == TokenKind_TokLParen) {
        p = tok_first.next_pos;
    }
        ParseResult init_res = collect_until_semi(src, p);
        p = init_res.next_pos;
        char* init_str = init_res.text;
        ParseResult cond_res2 = collect_until_semi(src, p);
        p = cond_res2.next_pos;
        char* cond_str = cond_res2.text;
        ParseResult iter_res = collect_until_brace(src, p);
        p = iter_res.next_pos;
        char* iter_str = iter_res.text;
        Token tok_maybe_rp = next_token(src, p);
        if (tok_maybe_rp.kind == TokenKind_TokRParen) {
        p = tok_maybe_rp.next_pos;
    }
        Token tok_lbrace_forc = next_token(src, p);
        p = tok_lbrace_forc.next_pos;
        char* for_body = "";
        while (true) {
        Token tok_for_peek = next_token(src, p);
        if (tok_for_peek.kind == TokenKind_TokRBrace || tok_for_peek.kind == TokenKind_TokEof) {
        p = tok_for_peek.next_pos;
        break;
    }
        StmtResult stmt_forc = parse_stmt(src, p);
        if (stmt_forc.next_pos <= p) {
        break;
    }
        p = stmt_forc.next_pos;
        for_body = stkt_format("%s    %s\n", for_body, stmt_forc.code);
    }
        ForNode n_for_c = (ForNode){init_str, cond_str, iter_str, for_body, p};
        return (StmtResult){gen_for(n_for_c), p};
    }
        if (tok.kind == TokenKind_TokLoop) {
        p = tok.next_pos;
        ParseResult times = parse_expr(src, p);
        p = times.next_pos;
        char* times_str = times.text;
        Token tok_next = next_token(src, p);
        char* step_str = "1";
        if (tok_next.kind == TokenKind_TokStep) {
        p = tok_next.next_pos;
        ParseResult step_res = parse_expr(src, p);
        p = step_res.next_pos;
        step_str = step_res.text;
    }
        Token tok_lbrace_loop = next_token(src, p);
        p = tok_lbrace_loop.next_pos;
        char* loop_body = "";
        while (true) {
        Token tok_peek_loop = next_token(src, p);
        if (tok_peek_loop.kind == TokenKind_TokRBrace || tok_peek_loop.kind == TokenKind_TokEof) {
        p = tok_peek_loop.next_pos;
        break;
    }
        StmtResult stmt_loop = parse_stmt(src, p);
        if (stmt_loop.next_pos <= p) {
        break;
    }
        p = stmt_loop.next_pos;
        loop_body = stkt_format("%s    %s\n", loop_body, stmt_loop.code);
    }
        LoopNode n_loop = (LoopNode){times_str, step_str, loop_body, p};
        return (StmtResult){gen_loop(n_loop), p};
    }
        if (tok.kind == TokenKind_TokMatch) {
        p = tok.next_pos;
        ParseResult match_cond_res = parse_expr(src, p);
        p = match_cond_res.next_pos;
        Token tok_match_lbrace = next_token(src, p);
        p = tok_match_lbrace.next_pos;
        char* all_cases = "";
        while (true) {
        Token tok_case_peek = next_token(src, p);
        if (tok_case_peek.kind == TokenKind_TokRBrace || tok_case_peek.kind == TokenKind_TokEof) {
        p = tok_case_peek.next_pos;
        break;
    }
        if (tok_case_peek.kind == TokenKind_TokCase) {
        p = tok_case_peek.next_pos;
        ParseResult val_res = parse_expr(src, p);
        p = val_res.next_pos;
        Token tok_c_lbrace = next_token(src, p);
        p = tok_c_lbrace.next_pos;
        char* case_body = "";
        while (true) {
        Token tok_b_peek = next_token(src, p);
        if (tok_b_peek.kind == TokenKind_TokRBrace || tok_b_peek.kind == TokenKind_TokEof) {
        p = tok_b_peek.next_pos;
        break;
    }
        StmtResult stmt_case = parse_stmt(src, p);
        if (stmt_case.next_pos <= p) {
        break;
    }
        p = stmt_case.next_pos;
        case_body = stkt_format("%s        %s\n", case_body, stmt_case.code);
    }
        CaseNode n_case = (CaseNode){val_res.text, case_body, false, p};
        char* c_code = gen_case(n_case);
        all_cases = stkt_format("%s%s", all_cases, c_code);
    }
        if (tok_case_peek.kind == TokenKind_TokDefault) {
        p = tok_case_peek.next_pos;
        Token tok_d_lbrace = next_token(src, p);
        p = tok_d_lbrace.next_pos;
        char* def_body = "";
        while (true) {
        Token tok_d_peek = next_token(src, p);
        if (tok_d_peek.kind == TokenKind_TokRBrace || tok_d_peek.kind == TokenKind_TokEof) {
        p = tok_d_peek.next_pos;
        break;
    }
        StmtResult stmt_def = parse_stmt(src, p);
        if (stmt_def.next_pos <= p) {
        break;
    }
        p = stmt_def.next_pos;
        def_body = stkt_format("%s        %s\n", def_body, stmt_def.code);
    }
        CaseNode n_def = (CaseNode){"", def_body, true, p};
        char* d_code = gen_case(n_def);
        all_cases = stkt_format("%s%s", all_cases, d_code);
    }
    }
        MatchNode n_match = (MatchNode){match_cond_res.text, all_cases, p};
        return (StmtResult){gen_match(n_match), p};
    }
        return (StmtResult){"", start};
}

ProcNode parse_proc(char* src, int32_t start) {
        int32_t p = start;
        Token tok_proc = next_token(src, p);
        p = tok_proc.next_pos;
        Token tok_name = next_token(src, p);
        p = tok_name.next_pos;
        Token tok_colon = next_token(src, p);
        p = tok_colon.next_pos;
        Token tok_ret = next_token(src, p);
        p = tok_ret.next_pos;
        char* ret_type_name = tok_ret.text;
        if (tok_ret.kind == TokenKind_TokLBracket) {
        Token ret_elem = next_token(src, p);
        p = ret_elem.next_pos;
        Token ret_rb = next_token(src, p);
        p = ret_rb.next_pos;
        ret_type_name = stkt_format("stkt_slice_%s", ret_elem.text);
    }
        Token tok_lparen = next_token(src, p);
        p = tok_lparen.next_pos;
        char* params_str = "";
        bool has_param = false;
        Token tok_first = next_token(src, p);
        if (tok_first.kind != TokenKind_TokRParen) {
        while (true) {
        Token p_name = next_token(src, p);
        p = p_name.next_pos;
        Token p_colon = next_token(src, p);
        p = p_colon.next_pos;
        Token p_type = next_token(src, p);
        p = p_type.next_pos;
        char* c_type = "";
        if (p_type.kind == TokenKind_TokLBracket) {
        Token elem_tok = next_token(src, p);
        p = elem_tok.next_pos;
        Token rb_tok = next_token(src, p);
        p = rb_tok.next_pos;
        c_type = stkt_format("stkt_slice_%s", elem_tok.text);
    }
        if (p_type.kind != TokenKind_TokLBracket) {
        c_type = to_c_type(p_type.text);
    }
        if (has_param) {
        params_str = stkt_format("%s, %s %s", params_str, c_type, p_name.text);
    }
        if ((!has_param)) {
        params_str = stkt_format("%s %s", c_type, p_name.text);
        has_param = true;
    }
        Token sep = next_token(src, p);
        p = sep.next_pos;
        if (sep.kind == TokenKind_TokRParen) {
        break;
    }
    }
    }
        if (tok_first.kind == TokenKind_TokRParen) {
        p = tok_first.next_pos;
    }
        Token tok_lbrace = next_token(src, p);
        p = tok_lbrace.next_pos;
        char* body_str = "";
        while (true) {
        Token tok_peek = next_token(src, p);
        if (tok_peek.kind == TokenKind_TokRBrace || tok_peek.kind == TokenKind_TokEof) {
        p = tok_peek.next_pos;
        break;
    }
        StmtResult stmt = parse_stmt(src, p);
        if (stmt.next_pos <= p) {
        break;
    }
        p = stmt.next_pos;
        body_str = stkt_format("%s    %s\n", body_str, stmt.code);
    }
        return (ProcNode){tok_name.text, ret_type_name, params_str, body_str, p};
}

char* extract_lambdas(char* src) {
        int32_t p = 0;
        char* out = "";
        char* l_id = "0";
        while (true) {
        Token tok = next_token(src, p);
        if (tok.kind == TokenKind_TokEof) {
        break;
    }
        if (tok.kind == TokenKind_TokLambda) {
        p = tok.next_pos;
        Token tok_col = next_token(src, p);
        p = tok_col.next_pos;
        Token ret_t = next_token(src, p);
        p = ret_t.next_pos;
        char* c_ret = to_c_type(ret_t.text);
        Token tok_lp = next_token(src, p);
        p = tok_lp.next_pos;
        char* params_str = "";
        bool has_param = false;
        Token tok_first_param = next_token(src, p);
        if (tok_first_param.kind != TokenKind_TokRParen) {
        while (true) {
        Token p_name = next_token(src, p);
        p = p_name.next_pos;
        Token p_col = next_token(src, p);
        p = p_col.next_pos;
        Token p_type = next_token(src, p);
        p = p_type.next_pos;
        char* c_type = to_c_type(p_type.text);
        if (has_param) {
        params_str = stkt_format("%s, %s %s", params_str, c_type, p_name.text);
    }
        if ((!has_param)) {
        params_str = stkt_format("%s %s", c_type, p_name.text);
        has_param = true;
    }
        Token sep = next_token(src, p);
        p = sep.next_pos;
        if (sep.kind == TokenKind_TokRParen) {
        break;
    }
    }
    }
        if (tok_first_param.kind == TokenKind_TokRParen) {
        p = tok_first_param.next_pos;
    }
        Token tok_lb = next_token(src, p);
        p = tok_lb.next_pos;
        char* body_str = "";
        while (true) {
        Token peek = next_token(src, p);
        if (peek.kind == TokenKind_TokRBrace || peek.kind == TokenKind_TokEof) {
        p = peek.next_pos;
        break;
    }
        StmtResult lam_stmt = parse_stmt(src, p);
        if (lam_stmt.next_pos <= p) {
        break;
    }
        p = lam_stmt.next_pos;
        body_str = stkt_format("%s    %s\n", body_str, lam_stmt.code);
    }
        LambdaNode node_lam = (LambdaNode){l_id, ret_t.text, params_str, body_str, p};
        char* def_code = gen_lambda(node_lam);
        out = stkt_format("%s%s\n", out, def_code);
    }
        if (tok.kind != TokenKind_TokLambda) {
        p = tok.next_pos;
    }
    }
        return out;
}

ProgramParts parse_program_defs(char* src, char* alias, stkt_slice_str synced_files) {
        int32_t p = 0;
        char* types = "";
        char* decls = "";
        char* procs = extract_lambdas(src);
        while (true) {
        Token tok = next_token(src, p);
        if (tok.kind == TokenKind_TokEof) {
        break;
    }
        if (tok.kind == TokenKind_TokExport || (strcmp(tok.text, "export") == 0)) {
        p = tok.next_pos;
        tok = next_token(src, p);
        if (tok.kind != TokenKind_TokProc && tok.kind != TokenKind_TokType && tok.kind != TokenKind_TokEnum) {
        p = tok.next_pos;
        tok = next_token(src, p);
    }
    }
        if (tok.kind == TokenKind_TokType) {
        TypeDeclNode n_type = parse_typedecl(src, p);
        p = n_type.next;
        char* type_c = gen_typedecl(n_type);
        types = stkt_format("%s%s\n", types, type_c);
    }
        if (tok.kind == TokenKind_TokEnum) {
        EnumNode n_enum = parse_enum(src, p);
        p = n_enum.next;
        char* enum_c = gen_enum(n_enum);
        types = stkt_format("%s%s\n", types, enum_c);
    }
        if (tok.kind == TokenKind_TokSync) {
        SyncNode n_sync = parse_sync(src, p);
        p = n_sync.next;
        char* mod_file = n_sync.module_path;
        char* sync_key = stkt_format("%s:%s", n_sync.alias, mod_file);
        if ((!is_already_sync(synced_files, sync_key))) {
        STKT_SLICE_APPEND(synced_files, sync_key);
        char* mod_code = read_text(mod_file);
        if (((int32_t)strlen(mod_code)) > 0) {
        ProgramParts sub = parse_program_defs(mod_code, n_sync.alias, synced_files);
        types = stkt_format("%s%s\n", types, sub.types);
        decls = stkt_format("%s%s\n", decls, sub.decls);
        procs = stkt_format("%s%s\n", procs, sub.procs);
    }
    }
    }
        if (tok.kind == TokenKind_TokProc) {
        ProcNode n_proc = parse_proc(src, p);
        p = n_proc.next;
        char* c_ret = to_c_type(n_proc.ret_type);
        if (((int32_t)strlen(alias)) > 0) {
        char* proc_c_alias = gen_aliased_proc(n_proc, alias);
        procs = stkt_format("%s%s\n", procs, proc_c_alias);
        decls = stkt_format("%s%s %s_%s(%s);\n", decls, c_ret, alias, n_proc.name, n_proc.params);
    }
        if (((int32_t)strlen(alias)) == 0) {
        char* proc_c_norm = gen_proc(n_proc);
        procs = stkt_format("%s%s\n", procs, proc_c_norm);
        decls = stkt_format("%s%s %s(%s);\n", decls, c_ret, n_proc.name, n_proc.params);
    }
    }
        if (tok.kind != TokenKind_TokType && tok.kind != TokenKind_TokEnum && tok.kind != TokenKind_TokProc && tok.kind != TokenKind_TokSync) {
        StmtResult stmt = parse_stmt(src, p);
        if (stmt.next_pos <= p) {
        break;
    }
        p = stmt.next_pos;
    }
    }
        return (ProgramParts){types, decls, procs};
}

char* parse_program(char* src) {
        int32_t p = 0;
        char* procs_str = extract_lambdas(src);
        char* decls_str = "";
        char* main_str = "";
        char* types_str = "";
        stkt_slice_str synced_files;
    STKT_SLICE_INIT(synced_files);

        while (true) {
        Token tok = next_token(src, p);
        if (tok.kind == TokenKind_TokEof) {
        break;
    }
        if (tok.kind == TokenKind_TokExport || (strcmp(tok.text, "export") == 0)) {
        p = tok.next_pos;
        tok = next_token(src, p);
        if (tok.kind != TokenKind_TokProc && tok.kind != TokenKind_TokType && tok.kind != TokenKind_TokEnum) {
        p = tok.next_pos;
        tok = next_token(src, p);
    }
    }
        if (tok.kind == TokenKind_TokProc) {
        ProcNode n_proc = parse_proc(src, p);
        p = n_proc.next;
        char* proc_c = gen_proc(n_proc);
        procs_str = stkt_format("%s%s\n", procs_str, proc_c);
        char* c_ret = to_c_type(n_proc.ret_type);
        decls_str = stkt_format("%s%s %s(%s);\n", decls_str, c_ret, n_proc.name, n_proc.params);
    }
        if (tok.kind == TokenKind_TokType) {
        TypeDeclNode n_type = parse_typedecl(src, p);
        p = n_type.next;
        char* type_c = gen_typedecl(n_type);
        types_str = stkt_format("%s%s\n", types_str, type_c);
    }
        if (tok.kind == TokenKind_TokEnum) {
        EnumNode n_enum = parse_enum(src, p);
        p = n_enum.next;
        char* enum_c = gen_enum(n_enum);
        types_str = stkt_format("%s%s\n", types_str, enum_c);
    }
        if (tok.kind == TokenKind_TokSync) {
        SyncNode n_sync = parse_sync(src, p);
        p = n_sync.next;
        char* mod_file = n_sync.module_path;
        char* sync_key = stkt_format("%s:%s", n_sync.alias, mod_file);
        if ((!is_already_sync(synced_files, sync_key))) {
        STKT_SLICE_APPEND(synced_files, sync_key);
        char* mod_code = read_text(mod_file);
        if (((int32_t)strlen(mod_code)) > 0) {
        ProgramParts sub = parse_program_defs(mod_code, n_sync.alias, synced_files);
        types_str = stkt_format("%s%s\n", types_str, sub.types);
        decls_str = stkt_format("%s%s\n", decls_str, sub.decls);
        procs_str = stkt_format("%s%s\n", procs_str, sub.procs);
    }
    }
    }
        if (tok.kind != TokenKind_TokProc && tok.kind != TokenKind_TokType && tok.kind != TokenKind_TokEnum && tok.kind != TokenKind_TokSync) {
        StmtResult stmt = parse_stmt(src, p);
        if (stmt.next_pos <= p) {
        break;
    }
        p = stmt.next_pos;
        main_str = stkt_format("%s%s\n", main_str, stmt.code);
    }
    }
        char* full_defs = stkt_format("%s\n%s\n%s", types_str, decls_str, procs_str);
        return gen_program(full_defs, main_str);
}


int main(int argc, char** argv) {
    __stkt_argc = argc;
    __stkt_argv = argv;
    printf("%s\n", "========================================");
    printf("%s\n", "=== Stkt Self-Hosted Compiler (v1.0) ===");
    printf("%s\n", "========================================");
    stkt_slice_str args = get_args();
    int32_t count = arg_count();
    if (count <= 1 || (strcmp(args.buf->data[1], "-h") == 0) || (strcmp(args.buf->data[1], "--help") == 0)) {
        printf("%s\n", "Usage: stkt <command> [options]");
        printf("%s\n", "  stkt run <file.stkt>            compile and run immediately");
        printf("%s\n", "  stkt build <file.stkt> -o <bin> compile to standalone binary");
        stkt_exit(0);
    }
    char* mode = "run";
    char* source_file = "";
    char* output_bin = "output";
    if (count >= 5 && (strcmp(args.buf->data[3], "-o") == 0)) {
        output_bin = args.buf->data[4];
    }
    if ((strcmp(args.buf->data[1], "run") == 0)) {
        mode = "run";
        source_file = args.buf->data[2];
    } else {
        if ((strcmp(args.buf->data[1], "build") == 0)) {
        mode = "build";
        source_file = args.buf->data[2];
    } else {
        mode = "run";
        source_file = args.buf->data[1];
    }
    }
    char* program_source = read_text(source_file);
    char* full_c = parse_program(program_source);
    write_text("compiler/generated_output.c", full_c);
    char* cmd = "";
    if ((strcmp(mode, "build") == 0)) {
        cmd = stkt_str_concat("cc -O3 compiler/generated_output.c -o ", output_bin);
        system_cmd(cmd);
    } else {
        if ((strcmp(mode, "run") == 0)) {
        cmd = "cc -O3 compiler/generated_output.c -o .stkt_tmp && ./.stkt_tmp; rm -f .stkt_tmp";
        system_cmd(cmd);
    }
    }
    return 0;
}
