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

export default function RecentsPage() {
  const { loading, error, data } = useQuery<GetResortsData>(GET_RESORTS);
  const [selectedResorts, setSelectedResorts] = useState<string[]>([]);
  const [selectedLiftTypes, setSelectedLiftTypes] = useState<string[]>([]);
  const [selectedDifficulties, setSelectedDifficulties] = useState<string[]>([]);

  // Get lift type from resort data
  const getLiftType = (liftName: string, location: string): string | null => {
    const resort = data?.resorts?.find(r => r.location === location);
    const lift = resort?.lifts?.find(l => l.liftName === liftName);
    return lift?.liftType || null;
  };

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

  // Get unique lift types from the data
  const liftTypes = useMemo(() => {
    if (!data?.globalRecentlyOpened?.lifts) return [];
    const types = data.globalRecentlyOpened.lifts
      .map(lift => getLiftType(lift.name, lift.location))
      .filter((type): type is string => type !== null && type !== '');
    return [...new Set(types)].sort();
  }, [data]);

  // Get unique run difficulties from the data
  const runDifficulties = useMemo(() => {
    if (!data?.globalRecentlyOpened?.runs) return [];
    const difficulties = data.globalRecentlyOpened.runs
      .map(run => normalizeDifficulty(getRunDifficulty(run.name, run.location)))
      .filter(d => d !== 'Unknown');
    return [...new Set(difficulties)].sort();
  }, [data]);

  // Filter lifts based on selected resorts and lift types
  const filteredLifts = useMemo(() => {
    if (!data?.globalRecentlyOpened?.lifts) return [];
    
    return data.globalRecentlyOpened.lifts.filter(lift => {
      // Resort filter
      if (selectedResorts.length > 0 && !selectedResorts.includes(lift.location)) {
        return false;
      }
      // Lift type filter
      if (selectedLiftTypes.length > 0) {
        const liftType = getLiftType(lift.name, lift.location);
        if (!liftType || !selectedLiftTypes.includes(liftType)) {
          return false;
        }
      }
      return true;
    });
  }, [data, selectedResorts, selectedLiftTypes]);

  // Filter runs based on selected resorts and difficulties
  const filteredRuns = useMemo(() => {
    if (!data?.globalRecentlyOpened?.runs) return [];
    
    return data.globalRecentlyOpened.runs.filter(run => {
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
  }, [data, selectedResorts, selectedDifficulties]);

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
  const hasActiveFilters = selectedResorts.length > 0 || selectedLiftTypes.length > 0 || selectedDifficulties.length > 0;

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

          {/* Lift Type Filter */}
          <Box>
            <Text c="dimmed" size="sm" mb="sm" fw={500}>
              Filter by Lift Type
            </Text>
            <Chip.Group multiple value={selectedLiftTypes} onChange={setSelectedLiftTypes}>
              <Group gap="xs">
                {liftTypes.map((type) => (
                  <Chip
                    key={type}
                    value={type}
                    variant="outline"
                    color="teal"
                  >
                    {type}
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
              🚡 Lifts ({filteredLifts.length})
            </Title>
            <Stack gap="xs">
              {filteredLifts.map((lift, index) => {
                const liftType = getLiftType(lift.name, lift.location);
                return (
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
                        {liftType && (
                          <Badge variant="outline" color="gray" size="sm">
                            {liftType}
                          </Badge>
                        )}
                        <Badge variant="light" color="teal" size="sm">
                          {lift.dateOpened}
                        </Badge>
                      </Group>
                    </Group>
                  </Paper>
                );
              })}
            </Stack>
          </Box>

          {/* Runs Column */}
          <Box>
            <Title order={3} c="white" mb="md">
              ⛷️ Runs ({filteredRuns.length})
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
