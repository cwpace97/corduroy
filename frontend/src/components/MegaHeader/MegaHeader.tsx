'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Box,
  Burger,
  Button,
  Divider,
  Drawer,
  Group,
  ScrollArea,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import classes from './MegaHeader.module.css';

// Navigation configuration - add new pages here to automatically appear in the header
const navigationItems = [
  { label: 'Home', href: '/' },
  { label: 'Weather', href: '/weather' },
  { label: 'Recents', href: '/recents' },
  { label: 'Details', href: '/details' },
];

export function MegaHeader() {
  const [drawerOpened, { toggle: toggleDrawer, close: closeDrawer }] = useDisclosure(false);
  const pathname = usePathname();

  const navLinks = navigationItems.map((item) => (
    <Link
      key={item.href}
      href={item.href}
      className={`${classes.link} ${pathname === item.href ? classes.linkActive : ''}`}
    >
      {item.label}
    </Link>
  ));

  const drawerLinks = navigationItems.map((item) => (
    <Link
      key={item.href}
      href={item.href}
      className={`${classes.link} ${pathname === item.href ? classes.linkActive : ''}`}
      onClick={closeDrawer}
    >
      {item.label}
    </Link>
  ));

  return (
    <Box pb={60}>
      <header className={classes.header}>
        <Group justify="space-between" h="100%">

          <Group h="100%" gap={0} visibleFrom="sm">
            {navLinks}
          </Group>

          <Group visibleFrom="sm">
            <Button variant="default">Log in</Button>
            <Button>Sign up</Button>
          </Group>

          <Burger opened={drawerOpened} onClick={toggleDrawer} hiddenFrom="sm" />
        </Group>
      </header>

      <Drawer
        opened={drawerOpened}
        onClose={closeDrawer}
        size="100%"
        padding="md"
        title="Navigation"
        hiddenFrom="sm"
        zIndex={1000000}
      >
        <ScrollArea h="calc(100vh - 80px)" mx="-md">
          <Divider my="sm" />
          {drawerLinks}
          <Divider my="sm" />

          <Group justify="center" grow pb="xl" px="md">
            <Button variant="default">Log in</Button>
            <Button>Sign up</Button>
          </Group>
        </ScrollArea>
      </Drawer>
    </Box>
  );
}

