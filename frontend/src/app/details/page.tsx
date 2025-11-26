'use client';

import { useQuery } from '@apollo/client/react';
import { useState } from 'react';
import {
  Container,
  Title,
  Text,
  Table,
  Center,
  Loader,
  Alert,
  Stack,
  Button,
  Group,
  Badge,
  Anchor,
} from '@mantine/core';
import { IconArrowLeft, IconAlertCircle, IconArrowUp, IconArrowDown } from '@tabler/icons-react';
import Link from 'next/link';
import { GET_RESORTS_SUMMARY } from '@/graphql/queries';

type SortType = 'name' | 'liftsOpen' | 'liftsOpenPercent' | 'runsOpen' | 'runsOpenPercent' | null;
type SortDirection = 'asc' | 'desc';

interface RunsByDifficulty {
  green: number;
  blue: number;
  black: number;
  doubleBlack: number;
  terrainPark: number;
  other: number;
}

interface Resort {
  location: string;
  openLifts: number;
  totalLifts: number;
  openRuns: number;
  totalRuns: number;
  runsByDifficulty: RunsByDifficulty;
}

interface GetResortsSummaryData {
  resorts: Resort[];
}

export default function DetailsPage() {
  const { loading, error, data } = useQuery<GetResortsSummaryData>(GET_RESORTS_SUMMARY);
  const [sortBy, setSortBy] = useState<SortType>(null);
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  if (loading) {
    return (
      <Center h="calc(100vh - 120px)">
        <Stack align="center" gap="md">
          <Loader size="xl" color="blue" />
          <Text c="white" size="lg">Loading resort data...</Text>
        </Stack>
      </Center>
    );
  }

  if (error) {
    return (
      <Center h="calc(100vh - 120px)">
        <Alert
          icon={<IconAlertCircle size={16} />}
          title="Error loading resort data"
          color="red"
          variant="filled"
        >
          {error.message}
        </Alert>
      </Center>
    );
  }

  const handleSort = (type: SortType) => {
    if (sortBy === type) {
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else {
        setSortBy(null);
        setSortDirection('asc');
      }
    } else {
      setSortBy(type);
      const initialDirection = type === 'name' ? 'asc' : 'desc';
      setSortDirection(initialDirection);
    }
  };

  const getSortedResorts = (): Resort[] => {
    if (!data?.resorts) return [];
    
    const resortsCopy = [...data.resorts] as Resort[];
    
    if (!sortBy) return resortsCopy;
    
    return resortsCopy.sort((a, b) => {
      let compareValue = 0;
      
      switch (sortBy) {
        case 'name':
          compareValue = a.location.localeCompare(b.location);
          break;
        case 'liftsOpen':
          compareValue = a.openLifts - b.openLifts;
          break;
        case 'liftsOpenPercent':
          const aLiftsPercent = a.totalLifts > 0 ? (a.openLifts / a.totalLifts) * 100 : 0;
          const bLiftsPercent = b.totalLifts > 0 ? (b.openLifts / b.totalLifts) * 100 : 0;
          compareValue = aLiftsPercent - bLiftsPercent;
          break;
        case 'runsOpen':
          compareValue = a.openRuns - b.openRuns;
          break;
        case 'runsOpenPercent':
          const aRunsPercent = a.totalRuns > 0 ? (a.openRuns / a.totalRuns) * 100 : 0;
          const bRunsPercent = b.totalRuns > 0 ? (b.openRuns / b.totalRuns) * 100 : 0;
          compareValue = aRunsPercent - bRunsPercent;
          break;
        default:
          return 0;
      }
      
      return sortDirection === 'asc' ? compareValue : -compareValue;
    });
  };

  const getSortIcon = (type: SortType) => {
    if (sortBy !== type) return null;
    return sortDirection === 'asc' ? <IconArrowUp size={14} /> : <IconArrowDown size={14} />;
  };

  const rows = getSortedResorts().map((resort) => (
    <Table.Tr key={resort.location}>
      <Table.Td ta="center">
        <Badge
          color={resort.openLifts === 0 ? 'red' : 'green'}
          variant="filled"
          size="sm"
          circle
        >
          {' '}
        </Badge>
      </Table.Td>
      <Table.Td fw={500}>{resort.location}</Table.Td>
      <Table.Td ta="center">
        <Text component="span" fw={500}>{resort.openLifts}</Text>
        <Text component="span" c="dimmed" size="sm"> / {resort.totalLifts}</Text>
      </Table.Td>
      <Table.Td ta="center">
        <Text component="span" fw={500}>{resort.openRuns}</Text>
        <Text component="span" c="dimmed" size="sm"> / {resort.totalRuns}</Text>
      </Table.Td>
      <Table.Td ta="center" fw={500}>{resort.runsByDifficulty.green}</Table.Td>
      <Table.Td ta="center" fw={500}>{resort.runsByDifficulty.blue}</Table.Td>
      <Table.Td ta="center" fw={500}>{resort.runsByDifficulty.black}</Table.Td>
      <Table.Td ta="center" fw={500}>{resort.runsByDifficulty.doubleBlack}</Table.Td>
      <Table.Td ta="center" fw={500}>{resort.runsByDifficulty.terrainPark}</Table.Td>
    </Table.Tr>
  ));

  return (
    <Container size="xl" py="xl">
      <Stack gap="lg">
        <Anchor component={Link} href="/" c="dimmed">
          <Group gap="xs">
            <IconArrowLeft size={20} />
            <Text>Back to Dashboard</Text>
          </Group>
        </Anchor>

        <div>
          <Title order={1} c="white" mb="xs">
            Resort Details
          </Title>
          <Text c="dimmed">
            Condensed view of all resort information
          </Text>
        </div>

        <Group gap="xs">
          <Button
            variant={sortBy === 'name' ? 'filled' : 'default'}
            onClick={() => handleSort('name')}
            rightSection={getSortIcon('name')}
            size="sm"
          >
            Sort by Name
          </Button>
          <Button
            variant={sortBy === 'liftsOpen' ? 'filled' : 'default'}
            onClick={() => handleSort('liftsOpen')}
            rightSection={getSortIcon('liftsOpen')}
            size="sm"
          >
            Sort by Lifts Open
          </Button>
          <Button
            variant={sortBy === 'liftsOpenPercent' ? 'filled' : 'default'}
            onClick={() => handleSort('liftsOpenPercent')}
            rightSection={getSortIcon('liftsOpenPercent')}
            size="sm"
          >
            Sort by Lifts Open %
          </Button>
          <Button
            variant={sortBy === 'runsOpen' ? 'filled' : 'default'}
            onClick={() => handleSort('runsOpen')}
            rightSection={getSortIcon('runsOpen')}
            size="sm"
          >
            Sort by Runs Open
          </Button>
          <Button
            variant={sortBy === 'runsOpenPercent' ? 'filled' : 'default'}
            onClick={() => handleSort('runsOpenPercent')}
            rightSection={getSortIcon('runsOpenPercent')}
            size="sm"
          >
            Sort by Runs Open %
          </Button>
        </Group>

        <Table.ScrollContainer minWidth={800}>
          <Table striped highlightOnHover withTableBorder withColumnBorders>
            <Table.Thead>
              <Table.Tr>
                <Table.Th ta="center">Status</Table.Th>
                <Table.Th>Resort Name</Table.Th>
                <Table.Th ta="center">Lifts Open</Table.Th>
                <Table.Th ta="center">Runs Open</Table.Th>
                <Table.Th ta="center" bg="green.7" c="white">Green</Table.Th>
                <Table.Th ta="center" bg="blue.7" c="white">Blue</Table.Th>
                <Table.Th ta="center" bg="dark.8" c="white">Black</Table.Th>
                <Table.Th ta="center" bg="dark.9" c="white">Double Black</Table.Th>
                <Table.Th ta="center" bg="orange.7" c="white">Terrain Park</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>{rows}</Table.Tbody>
          </Table>
        </Table.ScrollContainer>

        {(!data?.resorts || data.resorts.length === 0) && (
          <Center mt="xl">
            <Stack align="center" gap="xs">
              <Text c="dimmed" size="xl">No resort data available</Text>
              <Text c="dimmed">Run the scrapers to collect data</Text>
            </Stack>
          </Center>
        )}
      </Stack>
    </Container>
  );
}
