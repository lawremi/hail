require('dotenv').config();

const polka = require('polka');
const jwksRsa = require('jwks-rsa');
const jwt = require('jsonwebtoken');

const { AUTH0_DOMAIN, AUTH0_AUDIENCE } = process.env;
const AUTH0_ISSUER = `https://${AUTH0_DOMAIN}/`;

// Grabs public key, caches it, from Auth0's servers
// asymeetric signature used to ensure that not only the jwt was unmodified
// since signed, but that the issuer was Auth0 (since they hold the private key)
const jwksFn = jwksRsa({
  cache: true,
  rateLimit: true,
  jwksRequestsPerMinute: 5,
  jwksUri: `https://${AUTH0_DOMAIN}/.well-known/jwks.json`
});

// TODO: Validate audience, issuer

// Ref: https://github.com/auth0/node-jwks-rsa/blob/master/src/integrations/express.js
function getSecretKey(header, cb) {
  jwksFn.getSigningKey(header.kid, (err, key) => {
    if (err) {
      cb(err, null);
      return;
    }

    cb(null, key.publicKey || key.rsaPublicKey);
  });
}

// Verifies signature, as well as the issuer and audience, to guarantee
// that the token was truly for our resource server
const verifyToken = token =>
  new Promise((resolve, reject) => {
    jwt.verify(
      token,
      getSecretKey,
      {
        issuer: AUTH0_ISSUER,
        audience: AUTH0_AUDIENCE,
        clockTolerance: 2, // seconds to deal with clock skew
        algorithms: ['RS256']
      },
      (err, dToken) => {
        if (err) {
          console.error(err);
          return reject(err);
        }

        return resolve(dToken);
      }
    );
  });

const PORT = 8000;
// Polka is *mostly* express compatible, but let's not use unnecessary libraries
// better to understand the underlying security issues
// Best practices state that we should check the exact form of the auth header
// and if accepting from more than 1 place (say body or get query)
// make sure the token exists in only one place
// We have no need for this. Accept only from the header

// Also, I prefer not using middleware; call the functions needed inside the route
const bearerPrefix = 'Bearer ';
// naturally 1 past; so useful as end, and as the index to start reading token from
const bearerPrefixLen = bearerPrefix.length;
const getAuthToken = req => {
  // This is set from an "Authorization" header
  if (req.headers.authorization) {
    if (req.headers.authorization.substr(0, bearerPrefixLen) !== bearerPrefix) {
      return null;
    }

    const token = req.headers.authorization.substr(bearerPrefixLen);

    if (token.trim() === '') {
      return null;
    }

    return token;
  }

  return null;
};

async function attachTokenMiddleware(req, res, next) {
  const token = getAuthToken(req);

  if (!token) {
    next();
    return;
  }

  try {
    req.user = await verifyToken(token);
    next();
  } catch (_) {
    //TODO: Decide whether to return info to user
    const err = new Error('Unauthorized');
    err.code = 401;
    next(err);
  }
}

// x-requested-with for csrf, and for xmlhttp requests
// https://stackoverflow.com/questions/17478731/whats-the-point-of-the-x-requested-with-header
const corsMiddleware = (req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'Authorization, Content-Type, Content-Length, X-Requested-With'
  );
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');

  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  next();
};

polka()
  .use(corsMiddleware)
  .get('/notebook', attachTokenMiddleware, (req, res) => {
    console.info('token', req.user);
    res.end();
  })
  .listen(PORT, err => {
    if (err) {
      throw err;
    }

    console.info(`Auth server running on port ${PORT}`);
  });
