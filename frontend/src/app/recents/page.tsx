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
  Box,
  Chip,
} from '@mantine/core';
import { IconAlertCircle, IconMapPin } from '@tabler/icons-react';
import { GET_RESORTS } from '@/graphql/queries';
import { Resort } from '@/components/ResortCard/ResortCard';
import { RecentlyOpenedData } from '@/components/RecentlyOpened/RecentlyOpened';
import { PASS_OPTIONS, getResortPass } from '@/lib/constants';

interface GetResortsData {
  resorts: Resort[];
  globalRecentlyOpened: RecentlyOpenedData;
}

type TimePeriodFilter = 'all' | 'today' | 'last3days' | 'thisweek' | 'thismonth';

const TIME_PERIOD_OPTIONS: { value: TimePeriodFilter; label: string }[] = [
  { value: 'all', label: 'All Time' },
  { value: 'today', label: 'Today' },
  { value: 'last3days', label: 'Last 3 Days' },
  { value: 'thisweek', label: 'This Week' },
  { value: 'thismonth', label: 'This Month' },
];

export default function RecentsPage() {
  const { loading, error, data } = useQuery<GetResortsData>(GET_RESORTS);
  const [selectedPass, setSelectedPass] = useState<string>('all');
  const [selectedResorts, setSelectedResorts] = useState<string[]>([]);
  const [selectedLiftCategory, setSelectedLiftCategory] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
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

  // Get unique resort locations from the data (for MultiSelect - no 'all' option needed)
  const resortOptions = useMemo(() => {
    if (!data?.globalRecentlyOpened) return [];
    const liftsLocations = data.globalRecentlyOpened.lifts?.map(l => l.location) || [];
    const runsLocations = data.globalRecentlyOpened.runs?.map(r => r.location) || [];
    const locations = [...new Set([...liftsLocations, ...runsLocations])].sort();
    return locations.map(loc => ({ value: loc, label: loc }));
  }, [data]);

  // Get unique lift categories from the data, sorted by lift size (descending)
  const liftCategoryOptions = useMemo(() => {
    if (!data?.globalRecentlyOpened?.lifts) return [{ value: 'all', label: 'All Categories' }];
    
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
    
    return [
      { value: 'all', label: 'All Categories' },
      ...sortedCategories.map(cat => ({ value: cat, label: cat }))
    ];
  }, [data]);

  // Get unique run difficulties from the data
  const difficultyOptions = useMemo(() => {
    if (!data?.globalRecentlyOpened?.runs) return [{ value: 'all', label: 'All Difficulties' }];
    const difficulties = data.globalRecentlyOpened.runs
      .map(run => normalizeDifficulty(getRunDifficulty(run.name, run.location)))
      .filter(d => d !== 'Unknown');
    const uniqueDifficulties = [...new Set(difficulties)].sort();
    return [
      { value: 'all', label: 'All Difficulties' },
      ...uniqueDifficulties.map(diff => ({ value: diff, label: diff }))
    ];
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

  // Filter lifts based on selected pass, resorts, lift category, and time period
  const filteredLifts = useMemo(() => {
    if (!data?.globalRecentlyOpened?.lifts) return [];
    
    return data.globalRecentlyOpened.lifts.filter(lift => {
      // Time period filter
      if (!isWithinTimePeriod(lift.dateOpened, selectedTimePeriod)) {
        return false;
      }
      // Pass filter
      if (selectedPass !== 'all') {
        const pass = getResortPass(lift.location);
        if (pass !== selectedPass) {
          return false;
        }
      }
      // Resort filter (multi-select: empty array = show all)
      if (selectedResorts.length > 0 && !selectedResorts.includes(lift.location)) {
        return false;
      }
      // Lift category filter
      if (selectedLiftCategory !== 'all') {
        const liftCategory = lift.liftCategory || 'Unknown';
        if (liftCategory !== selectedLiftCategory) {
          return false;
        }
      }
      return true;
    });
  }, [data, selectedPass, selectedResorts, selectedLiftCategory, selectedTimePeriod]);

  // Filter runs based on selected pass, resorts, difficulty, and time period
  const filteredRuns = useMemo(() => {
    if (!data?.globalRecentlyOpened?.runs) return [];
    
    return data.globalRecentlyOpened.runs.filter(run => {
      // Time period filter
      if (!isWithinTimePeriod(run.dateOpened, selectedTimePeriod)) {
        return false;
      }
      // Pass filter
      if (selectedPass !== 'all') {
        const pass = getResortPass(run.location);
        if (pass !== selectedPass) {
          return false;
        }
      }
      // Resort filter (multi-select: empty array = show all)
      if (selectedResorts.length > 0 && !selectedResorts.includes(run.location)) {
        return false;
      }
      // Difficulty filter
      if (selectedDifficulty !== 'all') {
        const difficulty = normalizeDifficulty(getRunDifficulty(run.name, run.location));
        if (difficulty !== selectedDifficulty) {
          return false;
        }
      }
      return true;
    });
  }, [data, selectedPass, selectedResorts, selectedDifficulty, selectedTimePeriod]);

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
  const hasActiveFilters = selectedPass !== 'all' || selectedResorts.length > 0 || selectedLiftCategory !== 'all' || selectedDifficulty !== 'all' || selectedTimePeriod !== 'all';

  return (
    <Container fluid px={{ base: 8, sm: 32 }} py="md">
      <Title order={1} c="white" mb="md">
        Recently Opened
      </Title>
      <Text c="dimmed" mb="lg">
        Lifts and runs that have recently opened across all resorts
      </Text>

      {/* Filters Section */}
      <Stack gap="md" mb="lg">
        {/* Time Period Filter - Single Select */}
        <Box>
          <Text c="dimmed" size="sm" mb="xs" fw={500}>
            Time Opened
          </Text>
          <Chip.Group value={selectedTimePeriod} onChange={(value) => setSelectedTimePeriod(value as TimePeriodFilter)}>
            <Group gap="xs">
              {TIME_PERIOD_OPTIONS.map(option => (
                <Chip key={option.value} value={option.value} variant="outline" radius="sm">
                  {option.label}
                </Chip>
              ))}
            </Group>
          </Chip.Group>
        </Box>

        {/* Pass Filter - Single Select */}
        <Box>
          <Text c="dimmed" size="sm" mb="xs" fw={500}>
            Pass
          </Text>
          <Chip.Group value={selectedPass} onChange={(value) => setSelectedPass(value as string)}>
            <Group gap="xs">
              {PASS_OPTIONS.map(option => (
                <Chip key={option.value} value={option.value} variant="outline" radius="sm">
                  {option.label}
                </Chip>
              ))}
            </Group>
          </Chip.Group>
        </Box>

        {/* Resort Filter - Multi Select Chips (purple to distinguish from single-select) */}
        <Box>
          <Text c="dimmed" size="sm" mb="xs" fw={500}>
            Resorts {selectedResorts.length > 0 && `(${selectedResorts.length} selected)`}
          </Text>
          <Chip.Group multiple value={selectedResorts} onChange={setSelectedResorts}>
            <Group gap="xs">
              {resortOptions.map(option => (
                <Chip key={option.value} value={option.value} variant="outline" radius="sm" color="violet">
                  {option.label}
                </Chip>
              ))}
            </Group>
          </Chip.Group>
        </Box>

        {/* Lift Category Filter - Single Select */}
        <Box>
          <Text c="dimmed" size="sm" mb="xs" fw={500}>
            Lift Category
          </Text>
          <Chip.Group value={selectedLiftCategory} onChange={(value) => setSelectedLiftCategory(value as string)}>
            <Group gap="xs">
              {liftCategoryOptions.map(option => (
                <Chip key={option.value} value={option.value} variant="outline" radius="sm">
                  {option.label}
                </Chip>
              ))}
            </Group>
          </Chip.Group>
        </Box>

        {/* Run Difficulty Filter - Single Select */}
        <Box>
          <Text c="dimmed" size="sm" mb="xs" fw={500}>
            Run Difficulty
          </Text>
          <Chip.Group value={selectedDifficulty} onChange={(value) => setSelectedDifficulty(value as string)}>
            <Group gap="xs">
              {difficultyOptions.map(option => (
                <Chip key={option.value} value={option.value} variant="outline" radius="sm">
                  {option.label}
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
