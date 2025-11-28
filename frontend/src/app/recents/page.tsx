'use client';

import { useQuery } from '@apollo/client/react';
import { useState, useMemo } from 'react';
import {
  Container,
  Text,
  Title,
  Center,
  Loader,
  Alert,
  Stack,
  SimpleGrid,
  Paper,
  Badge,
  Group,
  Chip,
  Box,
} from '@mantine/core';
import { IconAlertCircle, IconMapPin } from '@tabler/icons-react';
import { GET_RESORTS } from '@/graphql/queries';
import { Resort } from '@/components/ResortCard/ResortCard';
import { RecentlyOpenedData } from '@/components/RecentlyOpened/RecentlyOpened';

interface GetResortsData {
  resorts: Resort[];
  globalRecentlyOpened: RecentlyOpenedData;
}

type TimePeriodFilter = 'all' | 'today' | 'last3days' | 'thisweek' | 'thismonth';

const TIME_PERIOD_OPTIONS: { value: TimePeriodFilter; label: string }[] = [
  { value: 'all', label: 'All Time' },
  { value: 'today', label: 'Opened Today' },
  { value: 'last3days', label: 'Last 3 Days' },
  { value: 'thisweek', label: 'This Week' },
  { value: 'thismonth', label: 'This Month' },
];

export default function RecentsPage() {
  const { loading, error, data } = useQuery<GetResortsData>(GET_RESORTS);
  const [selectedResorts, setSelectedResorts] = useState<string[]>([]);
  const [selectedLiftCategories, setSelectedLiftCategories] = useState<string[]>([]);
  const [selectedDifficulties, setSelectedDifficulties] = useState<string[]>([]);
  const [selectedTimePeriod, setSelectedTimePeriod] = useState<TimePeriodFilter>('all');

  // Get run difficulty from resort data
  const getRunDifficulty = (runName: string, location: string): string | null => {
    const resort = data?.resorts?.find(r => r.location === location);
    const run = resort?.runs?.find(r => r.runName === runName);
    return run?.runDifficulty || null;
  };

  // Normalize difficulty to a category
  const normalizeDifficulty = (difficulty: string | null): string => {
    if (!difficulty) return 'Unknown';
    const d = difficulty.toLowerCase();
    if (d.includes('green') || d.includes('easiest')) return 'Green';
    if (d.includes('blue') || d.includes('intermediate')) return 'Blue';
    if (d.includes('double') || d.includes('expert')) return 'Double Black';
    if (d.includes('black') || d.includes('advanced')) return 'Black';
    if (d.includes('park') || d.includes('terrain')) return 'Terrain Park';
    return 'Other';
  };

  // Get unique resort locations from the data
  const resortLocations = useMemo(() => {
    if (!data?.globalRecentlyOpened) return [];
    const liftsLocations = data.globalRecentlyOpened.lifts?.map(l => l.location) || [];
    const runsLocations = data.globalRecentlyOpened.runs?.map(r => r.location) || [];
    return [...new Set([...liftsLocations, ...runsLocations])].sort();
  }, [data]);

  // Get unique lift categories from the data, sorted by lift size (descending)
  const liftCategories = useMemo(() => {
    if (!data?.globalRecentlyOpened?.lifts) return [];
    
    // Build a map of category -> max size for that category
    const categoryToSize = new Map<string, number>();
    let hasUnknown = false;
    
    data.globalRecentlyOpened.lifts.forEach(lift => {
      if (!lift.liftCategory || lift.liftCategory === 'Unknown') {
        hasUnknown = true;
      } else {
        const currentSize = categoryToSize.get(lift.liftCategory) ?? 0;
        const liftSize = lift.liftSize ?? 0;
        if (liftSize > currentSize) {
          categoryToSize.set(lift.liftCategory, liftSize);
        }
      }
    });
    
    // Sort categories by size (descending), then add Unknown at the end if present
    const sortedCategories = Array.from(categoryToSize.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([category]) => category);
    
    if (hasUnknown) {
      sortedCategories.push('Unknown');
    }
    
    return sortedCategories;
  }, [data]);

  // Get unique run difficulties from the data
  const runDifficulties = useMemo(() => {
    if (!data?.globalRecentlyOpened?.runs) return [];
    const difficulties = data.globalRecentlyOpened.runs
      .map(run => normalizeDifficulty(getRunDifficulty(run.name, run.location)))
      .filter(d => d !== 'Unknown');
    return [...new Set(difficulties)].sort();
  }, [data]);

  // Helper function to parse date string as local date (YYYY-MM-DD format)
  // The database stores dates in America/Denver timezone as YYYY-MM-DD
  const parseDateAsLocal = (dateStr: string): Date => {
    // Parse YYYY-MM-DD format directly to avoid timezone issues
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day); // month is 0-indexed
  };

  // Get today's date in a comparable format (YYYY-MM-DD)
  const getTodayString = (): string => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // Helper function to check if a date falls within the selected time period
  const isWithinTimePeriod = (dateOpened: string, period: TimePeriodFilter): boolean => {
    if (period === 'all') return true;
    
    // Parse the opened date as local date components
    const openedDate = parseDateAsLocal(dateOpened);
    const now = new Date();
    
    // Get today at midnight (local time)
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    switch (period) {
      case 'today':
        // Compare date strings directly for most reliable comparison
        return dateOpened === getTodayString();
      
      case 'last3days': {
        const threeDaysAgo = new Date(today);
        threeDaysAgo.setDate(today.getDate() - 2); // Include today + 2 previous days = 3 days
        return openedDate >= threeDaysAgo && openedDate <= today;
      }
      
      case 'thisweek': {
        // Get Monday of current week
        const dayOfWeek = now.getDay();
        const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Sunday is 0
        const monday = new Date(today);
        monday.setDate(today.getDate() + mondayOffset);
        
        // Get Sunday of current week
        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        
        return openedDate >= monday && openedDate <= sunday;
      }
      
      case 'thismonth': {
        const firstOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
        const lastOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        return openedDate >= firstOfMonth && openedDate <= lastOfMonth;
      }
      
      default:
        return true;
    }
  };

  // Filter lifts based on selected resorts, lift categories, and time period
  const filteredLifts = useMemo(() => {
    if (!data?.globalRecentlyOpened?.lifts) return [];
    
    return data.globalRecentlyOpened.lifts.filter(lift => {
      // Time period filter
      if (!isWithinTimePeriod(lift.dateOpened, selectedTimePeriod)) {
        return false;
      }
      // Resort filter
      if (selectedResorts.length > 0 && !selectedResorts.includes(lift.location)) {
        return false;
      }
      // Lift category filter
      if (selectedLiftCategories.length > 0) {
        const liftCategory = lift.liftCategory || 'Unknown';
        if (!selectedLiftCategories.includes(liftCategory)) {
          return false;
        }
      }
      return true;
    });
  }, [data, selectedResorts, selectedLiftCategories, selectedTimePeriod]);

  // Filter runs based on selected resorts, difficulties, and time period
  const filteredRuns = useMemo(() => {
    if (!data?.globalRecentlyOpened?.runs) return [];
    
    return data.globalRecentlyOpened.runs.filter(run => {
      // Time period filter
      if (!isWithinTimePeriod(run.dateOpened, selectedTimePeriod)) {
        return false;
      }
      // Resort filter
      if (selectedResorts.length > 0 && !selectedResorts.includes(run.location)) {
        return false;
      }
      // Difficulty filter
      if (selectedDifficulties.length > 0) {
        const difficulty = normalizeDifficulty(getRunDifficulty(run.name, run.location));
        if (!selectedDifficulties.includes(difficulty)) {
          return false;
        }
      }
      return true;
    });
  }, [data, selectedResorts, selectedDifficulties, selectedTimePeriod]);

  const getDifficultyColor = (difficulty: string | null): string => {
    if (!difficulty) return 'gray';
    const d = difficulty.toLowerCase();
    if (d.includes('green') || d.includes('easiest')) return 'green';
    if (d.includes('blue') || d.includes('intermediate')) return 'blue';
    if (d.includes('double') || d.includes('expert')) return 'dark';
    if (d.includes('black') || d.includes('advanced')) return 'dark';
    if (d.includes('park') || d.includes('terrain')) return 'orange';
    return 'gray';
  };

  const getDifficultyLabel = (difficulty: string | null): string => {
    if (!difficulty) return '?';
    const d = difficulty.toLowerCase();
    if (d.includes('green') || d.includes('easiest')) return '●';
    if (d.includes('blue') && d.includes('2')) return '■■';
    if (d.includes('blue') || d.includes('intermediate')) return '■';
    if (d.includes('double') || d.includes('expert')) return '◆◆';
    if (d.includes('black') || d.includes('advanced')) return '◆';
    if (d.includes('park') || d.includes('terrain')) return '⬡';
    return '?';
  };

  const getDifficultyChipColor = (difficulty: string): string => {
    switch (difficulty) {
      case 'Green': return 'green';
      case 'Blue': return 'blue';
      case 'Black': return 'dark';
      case 'Double Black': return 'dark';
      case 'Terrain Park': return 'orange';
      default: return 'gray';
    }
  };

  if (loading) {
    return (
      <Center h="calc(100vh - 120px)">
        <Stack align="center" gap="md">
          <Loader size="xl" color="blue" />
          <Text c="white" size="lg">Loading recently opened data...</Text>
        </Stack>
      </Center>
    );
  }

  if (error) {
    return (
      <Center h="calc(100vh - 120px)">
        <Alert
          icon={<IconAlertCircle size={16} />}
          title="Error loading data"
          color="red"
          variant="filled"
        >
          {error.message}
        </Alert>
      </Center>
    );
  }

  const hasData = filteredLifts.length > 0 || filteredRuns.length > 0;
  const hasActiveFilters = selectedResorts.length > 0 || selectedLiftCategories.length > 0 || selectedDifficulties.length > 0 || selectedTimePeriod !== 'all';

  const handleTimePeriodChange = (value: string) => {
    setSelectedTimePeriod(value as TimePeriodFilter);
  };

  return (
    <Container fluid px="xl" py="md">
      <Title order={1} c="white" mb="md">
        Recently Opened
      </Title>
      <Text c="dimmed" mb="lg">
        Lifts and runs that have recently opened across all resorts
      </Text>

      {/* Filters Section */}
      <Paper
        p="md"
        mb="lg"
        radius="md"
        style={{
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Stack gap="md">
          {/* Time Period Filter */}
          <Box>
            <Group gap="xs" mb="sm">
              <Text c="dimmed" size="sm" fw={500}>
                Filter by Time Opened
              </Text>
            </Group>
            <Chip.Group multiple={false} value={selectedTimePeriod} onChange={handleTimePeriodChange}>
              <Group gap="xs">
                {TIME_PERIOD_OPTIONS.map((option) => (
                  <Chip
                    key={option.value}
                    value={option.value}
                    variant="outline"
                    color="violet"
                  >
                    {option.label}
                  </Chip>
                ))}
              </Group>
            </Chip.Group>
          </Box>

          {/* Resort Filter */}
          <Box>
            <Text c="dimmed" size="sm" mb="sm" fw={500}>
              Filter by Resort
            </Text>
            <Chip.Group multiple value={selectedResorts} onChange={setSelectedResorts}>
              <Group gap="xs">
                {resortLocations.map((location) => (
                  <Chip
                    key={location}
                    value={location}
                    variant="outline"
                    color="blue"
                  >
                    {location}
                  </Chip>
                ))}
              </Group>
            </Chip.Group>
          </Box>

          {/* Lift Category Filter */}
          <Box>
            <Text c="dimmed" size="sm" mb="sm" fw={500}>
              Filter by Lift Category
            </Text>
            <Chip.Group multiple value={selectedLiftCategories} onChange={setSelectedLiftCategories}>
              <Group gap="xs">
                {liftCategories.map((category) => (
                  <Chip
                    key={category}
                    value={category}
                    variant="outline"
                    color="teal"
                  >
                    {category}
                  </Chip>
                ))}
              </Group>
            </Chip.Group>
          </Box>

          {/* Run Difficulty Filter */}
          <Box>
            <Text c="dimmed" size="sm" mb="sm" fw={500}>
              Filter by Run Difficulty
            </Text>
            <Chip.Group multiple value={selectedDifficulties} onChange={setSelectedDifficulties}>
              <Group gap="xs">
                {runDifficulties.map((difficulty) => (
                  <Chip
                    key={difficulty}
                    value={difficulty}
                    variant="outline"
                    color={getDifficultyChipColor(difficulty)}
                  >
                    {difficulty}
                  </Chip>
                ))}
              </Group>
            </Chip.Group>
          </Box>

          {hasActiveFilters && (
            <Text c="dimmed" size="xs">
              Showing {filteredLifts.length} lifts and {filteredRuns.length} runs
            </Text>
          )}
        </Stack>
      </Paper>

      {!hasData ? (
        <Center mt="xl">
          <Stack align="center" gap="xs">
            <Text c="dimmed" size="xl">No recently opened data available</Text>
            <Text c="dimmed">Check back later or adjust your filters</Text>
          </Stack>
        </Center>
      ) : (
        <SimpleGrid cols={{ base: 1, md: 2 }} spacing="lg">
          {/* Lifts Column */}
          <Box>
            <Title order={3} c="white" mb="md">
              Lifts ({filteredLifts.length})
            </Title>
            <Stack gap="xs">
              {filteredLifts.map((lift, index) => (
                  <Paper
                    key={`${lift.location}-${lift.name}-${index}`}
                    p="sm"
                    radius="sm"
                    style={{
                      background: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                    }}
                  >
                    <Group justify="space-between" wrap="nowrap">
                      <Stack gap={4} style={{ flex: 1 }}>
                        <Text c="white" fw={500}>
                          {lift.name}
                        </Text>
                        <Group gap="xs">
                          <IconMapPin size={12} style={{ color: 'var(--mantine-color-dimmed)' }} />
                          <Text c="dimmed" size="xs">
                            {lift.location}
                          </Text>
                        </Group>
                      </Stack>
                      <Group gap="xs">
                        {lift.liftType && (
                          <Badge variant="outline" color="gray" size="sm">
                            {lift.liftType}
                          </Badge>
                        )}
                        <Badge variant="light" color="teal" size="sm">
                          {lift.dateOpened}
                        </Badge>
                      </Group>
                    </Group>
                  </Paper>
                ))}
            </Stack>
          </Box>

          {/* Runs Column */}
          <Box>
            <Title order={3} c="white" mb="md">
              Runs ({filteredRuns.length})
            </Title>
            <Stack gap="xs">
              {filteredRuns.map((run, index) => {
                const difficulty = getRunDifficulty(run.name, run.location);
                return (
                  <Paper
                    key={`${run.location}-${run.name}-${index}`}
                    p="sm"
                    radius="sm"
                    style={{
                      background: 'rgba(255, 255, 255, 0.03)',
                      border: '1px solid rgba(255, 255, 255, 0.08)',
                    }}
                  >
                    <Group justify="space-between" wrap="nowrap">
                      <Group gap="sm" style={{ flex: 1 }}>
                        <Badge
                          color={getDifficultyColor(difficulty)}
                          variant="filled"
                          size="sm"
                          fw={700}
                        >
                          {getDifficultyLabel(difficulty)}
                        </Badge>
                        <Stack gap={4}>
                          <Text c="white" fw={500}>
                            {run.name}
                          </Text>
                          <Group gap="xs">
                            <IconMapPin size={12} style={{ color: 'var(--mantine-color-dimmed)' }} />
                            <Text c="dimmed" size="xs">
                              {run.location}
                            </Text>
                          </Group>
                        </Stack>
                      </Group>
                      <Badge variant="light" color="blue" size="sm">
                        {run.dateOpened}
                      </Badge>
                    </Group>
                  </Paper>
                );
              })}
            </Stack>
          </Box>
        </SimpleGrid>
      )}
    </Container>
  );
}
