# Ponto de entrada Linux x86_64 da distribuição. Resolve o próprio diretório
# via /proc/self/exe, preserva argumentos e ambiente e invoca runtime/iniciar.
# Montado com as/ld do GNU binutils; não carrega bibliotecas compartilhadas.
.section .rodata
proc_exe: .asciz "/proc/self/exe"
script:   .asciz "runtime/iniciar"
.section .bss
.lcomm caminho, 4120

.section .text
.global _start
_start:
    mov $89, %eax                 # readlink
    lea proc_exe(%rip), %rdi
    lea caminho(%rip), %rsi
    mov $4096, %edx
    syscall
    cmp $0, %rax
    jle falha
    cmp $4096, %rax
    jae falha
    lea caminho(%rip), %rdi
    add %rax, %rdi
barra:
    dec %rdi
    cmpb $47, (%rdi)             # separador /
    jne barra
    inc %rdi
    lea script(%rip), %rsi
copiar:
    lodsb
    stosb
    test %al, %al
    jne copiar
    lea caminho(%rip), %rdi
    lea 8(%rsp), %rsi            # argv
    mov %rdi, (%rsi)
    mov (%rsp), %rax
    lea 16(%rsp,%rax,8), %rdx    # envp logo após argv[argc]
    mov $59, %eax                # execve
    syscall
falha:
    mov $127, %edi
    mov $60, %eax
    syscall

.section .note.GNU-stack,"",@progbits
