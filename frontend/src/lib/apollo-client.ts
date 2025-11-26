import { ApolloClient, InMemoryCache, HttpLink } from '@apollo/client/core';

const httpLink = new HttpLink({
  uri: 'http://localhost:8000/graphql',
});

export function makeClient() {
  return new ApolloClient({
    link: httpLink,
    cache: new InMemoryCache(),
  });
}
