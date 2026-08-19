#include "fake_clock.h"

#include "core/hw/clock.h"

static uint32_t g_now_ms;

void fake_clock_reset(void)
{
    g_now_ms = 0u;
}

void fake_clock_set(uint32_t ms)
{
    g_now_ms = ms;
}

void fake_clock_advance(uint32_t ms)
{
    g_now_ms += ms;
}

uint32_t hw_clock_now_ms(void)
{
    return g_now_ms;
}
