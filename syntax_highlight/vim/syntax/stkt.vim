" Vim syntax file for Stkt
" Language: Stkt (.stkt)
" Maintainer: Bennnto

if exists("b:current_syntax")
  finish
endif

" Keywords
syn keyword stktKeyword let const type sync export as
syn keyword stktKeyword if else while loop step for match case default return break continue
syn keyword stktDeclaration proc procedure L
syn keyword stktBuiltin onscreen onkey scan append len pop
syn keyword stktBoolean true false

" Types
syn keyword stktType i8 i16 i32 i64 u8 u16 u32 u64 f32 f64 int float bool char str void

" Comments
syn match stktComment "//.*$"
syn region stktComment start="/\*" end="\*/"

" Strings & Characters
syn region stktString start='"' end='"' contains=stktInterpolation,stktEscape
syn match stktCharacter "'\(\\[nrtvfb0\\'\"]\|x[0-9a-fA-F]\{2}\|.\)'"
syn match stktEscape "\\[nrtvfb0\\'\"]" contained
syn region stktInterpolation start="{" end="}" contained contains=ALLBUT,stktString

" Numbers
syn match stktNumber "\v\d+(\.\d+)?"
syn match stktNumber "\v0[xX][0-9a-fA-F]+"
syn match stktNumber "\v0[bB][01]+"

" Operators
syn match stktOperator "==\|!=\|<=\|>=\|<\|>\|&&\|||\|!\|+\|-\|\*\|/\|%\|&\||\|\^\|\~\|<<\|>>\|=\||>"

" Highlighting Links
hi def link stktKeyword Keyword
hi def link stktDeclaration Function
hi def link stktBuiltin Special
hi def link stktBoolean Boolean
hi def link stktType Type
hi def link stktComment Comment
hi def link stktString String
hi def link stktCharacter Character
hi def link stktEscape SpecialChar
hi def link stktInterpolation Identifier
hi def link stktNumber Number
hi def link stktOperator Operator

let b:current_syntax = "stkt"
