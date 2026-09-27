module.exports = grammar({
  name: 'stkt',

  extras: $ => [
    /\s/,
    $.comment,
  ],

  conflicts: $ => [
    [$.return_statement],
    [$._expression, $.expression_statement],
  ],

  rules: {
    source_file: $ => repeat($._statement),

    _statement: $ => choice(
      $.let_statement,
      $.const_statement,
      $.proc_declaration,
      $.export_statement,
      $.sync_statement,
      $.type_declaration,
      $.if_statement,
      $.while_statement,
      $.loop_statement,
      $.return_statement,
      $.expression_statement,
    ),

    comment: $ => token(choice(
      seq('//', /.*/),
      seq('/*', /[^*]*\*+([^/*][^*]*\*+)*/, '/')
    )),

    export_statement: $ => choice(
      seq('export', $.proc_declaration),
      seq('export', $.identifier)
    ),

    sync_statement: $ => seq(
      'sync',
      $.string,
      optional(seq('as', $.identifier))
    ),

    type_declaration: $ => seq(
      'type',
      $.identifier,
      '{',
      repeat(seq($.identifier, ':', $.type_name, optional(','))),
      '}'
    ),

    let_statement: $ => seq(
      'let',
      $.identifier,
      optional(seq(':', $.type_name)),
      optional(seq('=', $._expression))
    ),

    const_statement: $ => seq(
      'const',
      $.identifier,
      ':',
      $.type_name,
      '=',
      $._expression
    ),

    proc_declaration: $ => seq(
      choice('proc', 'procedure'),
      $.identifier,
      optional(seq(':', $.type_name)),
      $.parameter_list,
      $.block
    ),

    parameter_list: $ => seq(
      '(',
      optional(seq(
        $.parameter,
        repeat(seq(',', $.parameter))
      )),
      ')'
    ),

    parameter: $ => seq(
      $.identifier,
      ':',
      $.type_name
    ),

    block: $ => seq(
      '{',
      repeat($._statement),
      '}'
    ),

    if_statement: $ => seq(
      'if',
      $._expression,
      $.block,
      optional(seq('else', choice($.if_statement, $.block)))
    ),

    while_statement: $ => seq(
      'while',
      $._expression,
      $.block
    ),

    loop_statement: $ => seq(
      'loop',
      $._expression,
      optional(seq('step', $._expression)),
      $.block
    ),

    return_statement: $ => seq(
      'return',
      optional($._expression)
    ),

    expression_statement: $ => $._expression,

    _expression: $ => choice(
      $.identifier,
      $.number,
      $.string,
      $.char,
      $.boolean,
      $.call_expression,
      $.binary_expression,
      $.array_expression,
      $.member_expression,
      $.parenthesized_expression,
    ),

    parenthesized_expression: $ => seq('(', $._expression, ')'),

    array_expression: $ => seq(
      '[',
      optional(seq(
        $._expression,
        repeat(seq(',', $._expression))
      )),
      ']'
    ),

    call_expression: $ => prec(2, seq(
      choice($.identifier, $.builtin_function),
      '(',
      optional(seq(
        $._expression,
        repeat(seq(',', $._expression))
      )),
      ')'
    )),

    member_expression: $ => prec(3, seq(
      $._expression,
      '.',
      $.identifier
    )),

    binary_expression: $ => choice(
      prec.left(1, seq($._expression, choice('+', '-', '*', '/', '%', '==', '!=', '<', '<=', '>', '>=', '&&', '||', '|>', '=', '<<', '>>', '&', '|', '^'), $._expression))
    ),

    type_name: $ => choice(
      $.primitive_type,
      $.identifier,
      seq('[', $.type_name, ']')
    ),

    primitive_type: $ => token(choice(
      'i8', 'i16', 'i32', 'i64',
      'u8', 'u16', 'u32', 'u64',
      'f32', 'f64', 'int', 'float',
      'bool', 'char', 'str', 'void'
    )),

    builtin_function: $ => token(choice(
      'onscreen', 'onkey', 'scan', 'append', 'len', 'pop'
    )),

    boolean: $ => token(choice('true', 'false')),

    identifier: $ => /[a-zA-Z_][a-zA-Z0-9_]*/,

    number: $ => token(choice(
      /\d+(\.\d+)?/,
      /0[xX][0-9a-fA-F]+/,
      /0[bB][01]+/
    )),

    string: $ => token(seq('"', repeat(choice(/[^"\\\n]/, seq('\\', /./))), '"')),

    char: $ => token(seq("'", choice(/[^'\\\n]/, seq('\\', /./)), "'")),
  }
});
