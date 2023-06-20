import { graphql } from 'react-apollo';

gql`
`


gql`bla`


export const getUserByIdQuery = gql`
  query getUserById($id: ID) {
    user(id: $id) {
      ...userInfo
    }
  }
  ${userInfoFragment}
`;

const getUserByIdOptions = {
  options: ({ id }) => ({
    variables: {
      id,
    },
  }),
};

export const getUserByUsernameQuery = gql`
  query getUserByUsername($username: LowercaseString) {
    user(username: $username) {
      ...userInfo
    }
  }
  ${userInfoFragment}
`;