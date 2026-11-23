/*
 * lottery.c - a ticket-based (lottery) scheduler core in C.
 *
 * Implements the two-integer random-ticket selection of Waldspurger & Weihl,
 * compensation for clients that are behind, and a deterministic xorshift PRNG
 * so every experiment in the report is reproducible from a seed.
 *
 * Build:  gcc -O2 -std=c11 -Wall -Wextra -o lottery lottery.c
 * Run  :  ./lottery 1234 200
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#define MAX_CLIENTS 32
#define MAX_STEPS   2000000

typedef struct {
    char  name[16];
    int   tickets;      /* base ticket count (weight)          */
    int   effective;    /* tickets used for the next draw      */
    long  wins;         /* how often this client has won       */
} client_t;

typedef struct {
    client_t c[MAX_CLIENTS];
    int      n;
    int      compensation;   /* 0/1 */
    long     total_wins;
    uint64_t state;          /* xorshift64* state */
} lottery_t;

/* ---------------------------------------------------------------- PRNG */
static inline uint64_t next_rand(lottery_t *l)
{
    uint64_t x = l->state;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    l->state = x;
    return x * 2685821657736338717ULL;
}

/* Uniform in [0, total) without modulo bias (rejection sampling). */
static int draw_ticket(lottery_t *l, int total)
{
    uint64_t limit = UINT64_MAX - (UINT64_MAX % (uint64_t)total);
    uint64_t r;
    do {
        r = next_rand(l);
    } while (r >= limit);
    return (int)(r % (uint64_t)total);
}

/* ---------------------------------------------------------------- setup */
static void init(lottery_t *l, uint64_t seed, int compensation)
{
    memset(l, 0, sizeof(*l));
    l->state = seed ? seed : 0x9E3779B97F4A7C15ULL;
    l->compensation = compensation;
}

static int add_client(lottery_t *l, const char *name, int tickets)
{
    if (l->n >= MAX_CLIENTS || tickets < 0) return -1;
    client_t *c = &l->c[l->n];
    snprintf(c->name, sizeof(c->name), "%s", name);
    c->tickets = c->effective = tickets;
    c->wins = 0;
    return l->n++;
}

/* Recompute the effective ticket counts, applying compensation if enabled. */
static void update_weights(lottery_t *l)
{
    int total = 0, i;
    for (i = 0; i < l->n; i++) total += l->c[i].tickets;
    if (total == 0) return;

    for (i = 0; i < l->n; i++) {
        client_t *c = &l->c[i];
        if (!l->compensation || l->total_wins == 0) {
            c->effective = c->tickets;
            continue;
        }
        double expected = (double)c->tickets / (double)total * (double)l->total_wins;
        double lag = expected - (double)c->wins;
        if (lag >  8.0) lag =  8.0;
        if (lag < -8.0) lag = -8.0;
        double scaled = (double)c->tickets * pow(2.0, lag);
        c->effective = (int)(scaled + 0.5);
        if (c->effective < 0) c->effective = 0;
    }
}

/* ---------------------------------------------------------------- scheduler */
static int choose(lottery_t *l)
{
    int i, total = 0;
    update_weights(l);
    for (i = 0; i < l->n; i++) total += l->c[i].effective;
    if (total <= 0) return -1;

    int ticket = draw_ticket(l, total);
    int acc = 0;
    for (i = 0; i < l->n; i++) {
        acc += l->c[i].effective;
        if (ticket < acc) return i;
    }
    return l->n - 1;
}

static void run(lottery_t *l, long steps)
{
    long s;
    for (s = 0; s < steps; s++) {
        int w = choose(l);
        if (w < 0) return;
        l->c[w].wins++;
        l->total_wins++;
    }
}

/* ---------------------------------------------------------------- experiments */
static double share_error(lottery_t *l)
{
    int i, total = 0;
    double worst = 0.0;
    for (i = 0; i < l->n; i++) total += l->c[i].tickets;
    if (total == 0 || l->total_wins == 0) return 0.0;
    for (i = 0; i < l->n; i++) {
        double measured = (double)l->c[i].wins / (double)l->total_wins;
        double expected = (double)l->c[i].tickets / (double)total;
        double d = fabs(measured - expected);
        if (d > worst) worst = d;
    }
    return worst;
}

int main(int argc, char **argv)
{
    uint64_t seed = (argc > 1) ? strtoull(argv[1], NULL, 10) : 1234;
    int trials = (argc > 2) ? atoi(argv[2]) : 100;
    int comp, t;

    printf("seed=%llu trials=%d\n", (unsigned long long)seed, trials);
    printf("%-8s %-10s %-12s %-12s\n", "mode", "clients", "max_error", "worst_share");

    for (comp = 0; comp <= 1; comp++) {
        double sum_err = 0.0, worst = 0.0;
        for (t = 0; t < trials; t++) {
            lottery_t l;
            init(&l, seed + (uint64_t)t, comp);
            add_client(&l, "P0", 100);
            add_client(&l, "P1", 100);
            add_client(&l, "P2", 100);
            run(&l, 600);
            double e = share_error(&l);
            sum_err += e;
            if (e > worst) worst = e;
        }
        printf("%-8s %-10d %-12.6f %-12.6f\n", comp ? "compens." : "plain", 3,
               sum_err / trials, worst);
    }

    /* weighted experiment: 4:3:2:1 */
    {
        lottery_t l;
        init(&l, seed, 1);
        add_client(&l, "A", 400);
        add_client(&l, "B", 300);
        add_client(&l, "C", 200);
        add_client(&l, "D", 100);
        run(&l, 100000);
        printf("\nweighted run (100000 draws)\n");
        for (int i = 0; i < l.n; i++)
            printf("  %-3s tickets=%4d wins=%6ld share=%.4f\n",
                   l.c[i].name, l.c[i].tickets, l.c[i].wins,
                   (double)l.c[i].wins / (double)l.total_wins);
        printf("  max share error = %.6f\n", share_error(&l));
    }
    return 0;
}
