import { PureComponent } from 'react';
import auth from '../libs/auth';
// import cookie from '../libs/cookies';

declare type state = {
  password?: string;
  loggedIn?: boolean;
  failed?: boolean;
};

class Login extends PureComponent {
  state: state = {};

  static async getInitialProps(ctx: any) {
    if (ctx.req) {
      // Server side
      console.info('server', typeof window, ctx);
    } else {
      console.info('client', ctx);
    }
  }

  constructor(props: any) {
    super(props);

    // props.
  }

  onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({
      password: e.target.value
    });
  };

  onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const results = await auth.login(this.state.password);
      console.info('success!', results);
      this.setState({ loggedIn: true });
    } catch (e) {
      console.info(e);
      this.setState({ failed: true });
    }
  };

  render() {
    if (this.state.loggedIn) {
      return <div>Success!</div>;
    } else if (this.state.failed) {
      return <div>Unauthorized!</div>;
    }

    return (
      <span id="login">
        <h3>Login</h3>
        <span className="card">
          <button className="outlined-button">Login</button>
        </span>
        <span className="card">
          <form onSubmit={this.onSubmit}>
            <input type="password" onChange={this.onChange} />
          </form>
        </span>
      </span>
    );
  }
}

export default Login;
