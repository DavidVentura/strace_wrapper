# Strace wrapper

This tiny tool attempts to filter and pretty-print system calls that have failed. It is simply a wrapper on `strace`.

Example usage:

```
$ ./strace.py netcat -l -p 80
Executing 'bind' on '0.0.0.0' resulted in 'Permission denied'   Full args: (3, {sa_family=AF_INET, sin_port=htons(80), sin_addr=inet_addr("0.0.0.0")
```

```
$ ./strace.py cat /etc/shadow
Executing 'open' on '/etc/shadow' resulted in 'Permission denied'       Full args: ("/etc/shadow", O_RDONLY)
```

```
./strace.py rm -f /etc/hostname 
Executing 'unlinkat' on '/etc/hostname' resulted in 'Permission denied' Full args: (AT_FDCWD, "/etc/hostname", 0)
?? lseek(0, 0, SEEK_CUR)                   = -1 ESPIPE (Illegal seek)
```

On lines that do not match the specified regex you get the raw output prefixed with '??'
